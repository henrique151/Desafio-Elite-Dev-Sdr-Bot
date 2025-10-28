import os
import requests
import json
import logging
from dotenv import load_dotenv
from app.utils.date_utils import normalizar_data

load_dotenv()

PIPEFY_URL = "https://api.pipefy.com/graphql"
ACCESS_TOKEN = os.getenv("PIPEFY_ACCESS_TOKEN")
PIPE_ID = os.getenv("PIPEFY_PRE_SALES_PIPE_ID")

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Cache para os IDs dos campos
_field_id_cache = {}

# Modo simulação
SIMULATION_MODE = not ACCESS_TOKEN or "SIMULACAO" in ACCESS_TOKEN.upper()


def _executar_query(query: str, variables: dict = None) -> dict:
    """Executa uma query/mutation GraphQL no Pipefy."""
    logger.debug("Query Pipefy enviada: %s", query)
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables or {}}

    try:
        response = requests.post(
            PIPEFY_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        if "errors" in result:
            logger.error("Pipefy retornou erros: %s",
                         json.dumps(result["errors"], indent=2))
        return result
    except Exception as e:
        logger.error("Erro ao conectar com Pipefy: %s", e)
        return {"error": str(e)}


def _get_field_ids() -> dict:
    """Busca e cacheia os IDs dos campos do Start Form do Pipefy."""
    global _field_id_cache
    if _field_id_cache:
        return _field_id_cache

    query = """
    query GetPipeFields($pipeId: ID!) {
      pipe(id: $pipeId) {
        start_form_fields {
          id
          label
        }
      }
    }
    """
    variables = {"pipeId": PIPE_ID}
    result = _executar_query(query, variables)

    if result.get("error") or "errors" in result:
        raise Exception(
            "Não foi possível buscar os campos do Pipefy. Verifique o token e o ID do Pipe.")

    fields = result.get("data", {}).get(
        "pipe", {}).get("start_form_fields", [])
    if not fields:
        raise Exception("Nenhum campo encontrado no Start Form do Pipe.")

    label_map = {
        "Nome": "nome",
        "Email": "email",
        "Empresa": "empresa",
        "Necessidade": "necessidade",
        "Interesse_confirmado": "interesse",
        "Meeting_link": "link_reuniao",
        "Data Reuniao": "data_reuniao",
        "event_id": "event_id"
    }
    for field in fields:
        if field.get("label") in label_map:
            _field_id_cache[label_map[field["label"]]] = field.get("id")

    if len(_field_id_cache) < len(label_map):
        logger.warning("Nem todos os campos esperados foram encontrados no Pipefy: %s", list(
            _field_id_cache.keys()))

    return _field_id_cache


def buscar_card_por_email(email: str, after_cursor: str = None) -> dict | None:
    """Busca um card existente no Pipefy pelo e-mail."""
    after_clause = f', after: "{after_cursor}"' if after_cursor else ""
    query = f"""
        query {{
        allCards(pipeId: {PIPE_ID}, first: 50{after_clause}) {{
            pageInfo {{
            hasNextPage
            endCursor
            }}
            edges {{
            node {{
                id
                title
                fields {{
                name
                value
                }}
            }}
            }}
        }}
        }}
    """
    result = _executar_query(query)
    cards = result.get("data", {}).get("allCards", {}).get("edges", [])
    page_info = result.get("data", {}).get("allCards", {}).get("pageInfo", {})

    for edge in cards:
        node = edge["node"]
        for field in node.get("fields", []):
            if field.get("name", "").strip().lower() == "email" and field.get("value", "").strip().lower() == email.lower():
                logger.info("Card encontrado para e-mail %s: %s",
                            email, node["id"])
                return node

    if page_info.get("hasNextPage"):
        return buscar_card_por_email(email, after_cursor=page_info.get("endCursor"))

    logger.info("Nenhum card encontrado para e-mail %s", email)
    return None


def registrar_lead(nome: str, email: str, empresa: str, necessidade: str, datetime_str: str = None, link_reuniao: str = None, event_id: str = None) -> dict:
    """Cria um novo card (lead) no Pipefy ou atualiza se já existir."""

    if SIMULATION_MODE:
        return {"status": "simulacao", "card_id": "SIM_CARD_12345", "mensagem": "Simulação: lead registrado."}

    existente = buscar_card_por_email(email)
    if existente:
        card_id = existente["id"]
        logger.info("Lead existente, atualizando card %s", card_id)
        resultado_update = atualizar_card_com_reuniao(
            card_id, link_reuniao, datetime_str, event_id)
        return {"status": "atualizado", "card_id": card_id, "mensagem": "Card atualizado.", "detalhes": resultado_update}

    try:
        field_ids = _get_field_ids()
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

    if datetime_str:
        try:
            datetime_str = normalizar_data(datetime_str)
        except Exception as e:
            logger.warning("Falha ao normalizar data: %s", e)

    necessidade_map = {
        "implementar ia": "Implementar IA",
        "automacao de processos": "Automação de Processos",
        "integracao de sistemas": "Integração de Sistemas",
        "analise de dados": "Análise de Dados / BI",
        "otimizacao de vendas": "Otimização de Vendas",
        "marketing digital": "Marketing Digital",
        "atendimento ao cliente": "Atendimento ao Cliente / Suporte",
        "seguranca e compliance": "Segurança e Compliance",
        "infraestrutura e cloud": "Infraestrutura e Cloud",
        "treinamento e capacitacao": "Treinamento e Capacitação",
        "outros": "Outros"
    }

    necessidade_value = necessidade_map.get(
        necessidade.strip().lower(), "Outros")

    fields = [
        {"field_id": field_ids["nome"], "field_value": nome},
        {"field_id": field_ids["email"], "field_value": email},
        {"field_id": field_ids["empresa"], "field_value": empresa},
        {"field_id": field_ids["necessidade"],
            "field_value": necessidade_value},
        {"field_id": field_ids["interesse"], "field_value": "Sim"},
    ]

    if link_reuniao:
        fields.append(
            {"field_id": field_ids["link_reuniao"], "field_value": link_reuniao})
    if datetime_str:
        fields.append(
            {"field_id": field_ids["data_reuniao"], "field_value": datetime_str})
    if event_id:
        fields.append(
            {"field_id": field_ids["event_id"], "field_value": event_id})

    mutation = """
    mutation CreateCard($input: CreateCardInput!) {
      createCard(input: $input) {
        card { id title }
      }
    }
    """
    variables = {"input": {"pipe_id": PIPE_ID, "fields_attributes": fields}}
    result = _executar_query(mutation, variables)

    card_data = result.get("data", {}).get("createCard", {}).get("card")
    if card_data:
        return {"status": "criado", "card_id": card_data["id"], "mensagem": "Lead registrado com sucesso."}
    return {"status": "falha", "mensagem": "Falha ao criar card.", "detalhes": result}


def registrar_ou_atualizar_lead(email: str, datetime_str: str = None, link_reuniao: str = None):
    existente = buscar_card_por_email(email)
    if existente:
        card_id = existente["id"]
        print(f"[INFO] Lead existente: atualizando card {card_id}")
        resultado_update = atualizar_card_com_reuniao(
            card_id, link_reuniao, datetime_str)
        return json.dumps({
            "status": "atualizado",
            "card_id": card_id,
            "email": email,
            "mensagem": "Lead existente atualizado com sucesso.",
            "detalhes": resultado_update
        })

    print(
        f"[INFO] Nenhum card encontrado para o e-mail {email}. Não será criado novo card.")
    return json.dumps({
        "status": "nao_encontrado",
        "email": email,
        "mensagem": "Nenhum card encontrado com este e-mail. Não foi criado card novo."
    })


def buscar_event_id_do_card(card_id: str) -> str | None:
    """
    Retorna o event_id do Google Calendar salvo no Pipefy, se existir.
    Procura pelo campo 'event_id'.
    """
    from app.services.pipefy_service import _executar_query

    # Monta query para buscar o card pelo ID
    query = f"""
    query {{
      card(id: "{card_id}") {{
        id
        fields {{
          name
          value
        }}
      }}
    }}
    """

    result = _executar_query(query)
    card = result.get("data", {}).get("card")
    if not card:
        return None

    for f in card.get("fields", []):
        if f.get("name", "").strip().lower() == "event_id":
            return f.get("value")

    return None


def atualizar_card_com_reuniao(card_id: str = None, link: str = None, datetime_str: str = None, event_id: str = None, email: str = None) -> dict:
    """Atualiza campos de reunião de um card no Pipefy."""

    if not card_id:
        if not email:
            return {"status": "erro", "mensagem": "Informe card_id ou email"}
        existente = buscar_card_por_email(email)
        if existente:
            card_id = existente["id"]
            logger.info("Card real encontrado pelo e-mail %s: %s",
                        email, card_id)
        else:
            return {"status": "erro", "mensagem": f"Nenhum card encontrado para o e-mail {email}"}

    if SIMULATION_MODE:
        return {"status": "simulacao", "card_id": card_id, "mensagem": "Simulação: card atualizado."}

    try:
        field_ids = _get_field_ids()
    except Exception as e:
        return {"status": "erro", "mensagem": str(e)}

    values = []
    if link and "link_reuniao" in field_ids:
        values.append({"fieldId": field_ids["link_reuniao"], "value": link})
    if datetime_str and "data_reuniao" in field_ids:
        values.append(
            {"fieldId": field_ids["data_reuniao"], "value": normalizar_data(datetime_str)})
    if event_id and "event_id" in field_ids:  # ✅ Adicionado event_id
        values.append({"fieldId": field_ids["event_id"], "value": event_id})

    if not values:
        return {"status": "nada_para_atualizar", "mensagem": "Nenhum campo informado para atualização."}

    mutation = """
    mutation UpdateCardFields($input: UpdateFieldsValuesInput!) {
      updateFieldsValues(input: $input) {
        success
      }
    }
    """
    variables = {"input": {"nodeId": card_id, "values": values}}
    result = _executar_query(mutation, variables)

    success = result.get("data", {}).get(
        "updateFieldsValues", {}).get("success")
    return {"status": "sucesso" if success else "falha", "card_id": card_id, "detalhes": result}
