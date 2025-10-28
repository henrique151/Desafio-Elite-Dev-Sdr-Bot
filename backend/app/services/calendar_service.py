from pydantic import BaseModel
import os
import pickle
import pytz
import logging
from datetime import datetime, timedelta
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.services.pipefy_service import atualizar_card_com_reuniao
from app.utils.google_credentials import build_credentials_file
from app.utils.date_utils import normalizar_data
from google.oauth2.service_account import Credentials

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
CREDENTIALS_FILE = os.getenv(
    "GOOGLE_OAUTH_CREDENTIALS", "app/credentials/credentials.json")
TOKEN_FILE = os.getenv("GOOGLE_OAUTH_TOKEN", "app/credentials/token.pkl")
TIMEZONE = "America/Sao_Paulo"

# key_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY_PATH")
# creds = Credentials.from_service_account_file(key_path, scopes=SCOPES)
# service = build("calendar", "v3", credentials=creds)


def get_google_calendar_service():
    key_content = os.environ.get("GOOGLE_SERVICE_ACCOUNT_KEY")
    if not key_content:
        raise ValueError(
            "A variável de ambiente GOOGLE_SERVICE_ACCOUNT_KEY não está definida")

    key_path = "/tmp/service_account.json"
    with open(key_path, "w") as f:
        f.write(key_content)

    creds = Credentials.from_service_account_file(key_path, scopes=SCOPES)
    service = build("calendar", "v3", credentials=creds)
    return service


service = get_google_calendar_service()


def _to_dt(iso_str):
    # garante timezone-aware
    dt = datetime.fromisoformat(iso_str)
    if dt.tzinfo is None:
        tz = pytz.timezone(TIMEZONE)
        dt = tz.localize(dt)
    return dt


def verificar_disponibilidade(start_time_iso: str, duracao_horas: int = 1) -> bool:
    """Retorna True se livre no calendário para o intervalo dado."""
    start = _to_dt(start_time_iso)
    end = start + timedelta(hours=duracao_horas)

    try:
        events = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        return len(events) == 0
    except HttpError as e:
        raise Exception(f"Erro ao verificar disponibilidade: {e}")


def agendar_evento(nome_cliente: str, email: str, start_time_str: str, duracao_horas: int = 1, card_id: str = None):
    """Agenda evento e retorna meeting_link, meeting_datetime(iso) e eventId."""
    start_time_iso = normalizar_data(start_time_str)
    start = _to_dt(start_time_iso)
    end = start + timedelta(hours=duracao_horas)

    event = {
        'summary': f'Reunião com {nome_cliente} - Elite Dev - {card_id}',
        'description': f'Reunião com {nome_cliente}',
        'start': {'dateTime': start.isoformat(), 'timeZone': TIMEZONE},
        'end': {'dateTime': end.isoformat(), 'timeZone': TIMEZONE},
        'attendees': [{'email': email}],
        'conferenceData': {'createRequest': {'requestId': f"meet-{int(start.timestamp())}"}}
    }

    evento = service.events().insert(
        calendarId=CALENDAR_ID,
        body=event,
        conferenceDataVersion=1
    ).execute()

    print(evento["id"])
    print(evento["hangoutLink"])

    meeting_link = None
    conference = evento.get('conferenceData', {})

    for ep in conference.get('entryPoints', []):
        if ep.get('entryPointType') == 'video' or 'meet' in (ep.get('uri') or ''):
            meeting_link = ep.get('uri')
            break

    return {"meeting_link": meeting_link, "meeting_datetime": start_time_iso, "event_id": evento.get('id')}


def cancelar_evento(event_id: str):
    """Remove evento do Google Calendar (se existir)."""
    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
        return {"status": "cancelado", "event_id": event_id}
    except HttpError as e:
        if e.resp.status == 404:
            return {"status": "nao_encontrado", "event_id": event_id}
        raise


def buscar_horarios_disponiveis(dias: int = 7, qtd: int = 3, inicio_hora: int = 9, fim_hora: int = 18, duracao_horas: int = 1, fuso_horario: str = TIMEZONE):
    tz = pytz.timezone(fuso_horario)
    agora = datetime.now(tz).replace(minute=0, second=0, microsecond=0)
    fim = agora + timedelta(days=dias)

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=agora.isoformat(),
        timeMax=fim.isoformat(),
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    eventos = events_result.get('items', [])
    horarios = []
    for dia in range(dias):
        dia_atual = (agora + timedelta(days=dia)).replace(hour=inicio_hora)
        for hora in range(inicio_hora, fim_hora):
            slot = dia_atual.replace(hour=hora, minute=0)
            start_iso = slot.isoformat()
            if verificar_disponibilidade(start_iso, duracao_horas):
                horarios.append(slot)
            if len(horarios) >= qtd:
                break
        if len(horarios) >= qtd:
            break

    horarios = sorted(horarios)[:qtd]
    return [{"label": h.strftime("%d/%m/%Y %H:%M"), "iso": h.isoformat()} for h in horarios]


def tentar_agendar_ou_sugerir(
    card_id: str,
    nome_cliente: str,
    email: str,
    empresa_cliente: str,
    necessidade_cliente: str,
    proposed_iso: str,
    duracao_horas: int = 1,
    proximidade_minutos: int = 60,
    sugestoes_qtd: int = 3
):
    from app.services.pipefy_service import buscar_card_por_email, registrar_lead, atualizar_card_com_reuniao

    proposed_iso_norm = normalizar_data(proposed_iso)

    if verificar_disponibilidade(proposed_iso_norm, duracao_horas):
        ag = agendar_evento(nome_cliente, email,
                            proposed_iso_norm, duracao_horas)

        existente = buscar_card_por_email(email)
        if existente:
            resultado_pipefy = atualizar_card_com_reuniao(
                existente["id"], ag["meeting_link"], ag["meeting_datetime"], ag["event_id"]
            )
        else:
            resultado_pipefy = registrar_lead(
                nome=nome_cliente,
                email=email,
                empresa=empresa_cliente,
                necessidade=necessidade_cliente,
                datetime_str=ag["meeting_datetime"],
                link_reuniao=ag["meeting_link"]
            )

        return {
            "status": "agendado",
            "meeting_link": ag["meeting_link"],
            "meeting_datetime": ag["meeting_datetime"],
            "event_id": ag["event_id"],
            "pipefy": resultado_pipefy
        }

    base = _to_dt(proposed_iso_norm)
    suggestions = []
    step = proximidade_minutos
    attempts = 1
    while len(suggestions) < sugestoes_qtd and attempts <= 24:
        for candidate in (base + timedelta(minutes=step*attempts), base - timedelta(minutes=step*attempts)):
            cand_iso = candidate.isoformat()
            if verificar_disponibilidade(cand_iso, duracao_horas):
                suggestions.append({"label": candidate.strftime(
                    "%d/%m/%Y %H:%M"), "iso": cand_iso})
                if len(suggestions) >= sugestoes_qtd:
                    break
        attempts += 1

    return {"status": "ocupado", "mensagem": "Horário não disponível", "sugestoes": suggestions}


def agendar_e_atualizar_pipefy(card_id: str, nome_cliente: str, email: str, start_time_str: str, duracao_horas: int = 1):
    from app.services.calendar_service import cancelar_evento, agendar_evento
    from app.services.pipefy_service import buscar_event_id_do_card, atualizar_card_com_reuniao

    antigo_event_id = buscar_event_id_do_card(card_id)
    print(f"[DEBUG] antigo_event_id: {antigo_event_id}")

    if antigo_event_id:
        try:
            cancelar_evento(antigo_event_id)
            print(f"[INFO] Evento antigo {antigo_event_id} cancelado")
        except Exception as e:
            print(
                f"[WARNING] Falha ao cancelar evento antigo ({antigo_event_id}): {e}")

    agendamento = agendar_evento(
        nome_cliente, email, start_time_str, duracao_horas)
    print(f"[INFO] Novo evento agendado: {agendamento}")

    try:
        resultado_pipefy = atualizar_card_com_reuniao(
            card_id, agendamento["meeting_link"], agendamento["meeting_datetime"], agendamento["event_id"]
        )
        print(f"[INFO] Pipefy atualizado: {resultado_pipefy}")
    except Exception as e:
        print(f"[ERROR] Falha ao atualizar Pipefy: {e}")
        resultado_pipefy = {"status": "falha", "mensagem": str(e)}

    return {
        "status": "sucesso",
        "meeting_link": agendamento["meeting_link"],
        "meeting_datetime": agendamento["meeting_datetime"],
        "event_id": agendamento["event_id"],
        "pipefy_result": resultado_pipefy
    }


def agendar_reuniao(card_id: str, nome_cliente: str, email: str, start_time_iso: str):
    resultado = agendar_e_atualizar_pipefy(
        card_id, nome_cliente, email, start_time_iso)
    return resultado


oferecer_horarios = buscar_horarios_disponiveis
