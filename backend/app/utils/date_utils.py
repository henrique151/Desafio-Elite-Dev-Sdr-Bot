import dateparser
from datetime import datetime
import pytz


def normalizar_data(texto_data: str) -> str:
    """
    Converte uma data em formato natural ou ISO para o formato ISO 8601
    ajustado para o fuso horário America/Sao_Paulo.
    """

    if not texto_data or not isinstance(texto_data, str):
        raise ValueError("Data inválida ou vazia.")

    tz_sp = pytz.timezone("America/Sao_Paulo")
   
    try:
        parsed_date = datetime.fromisoformat(texto_data)
        if parsed_date.tzinfo is None:
            parsed_date = tz_sp.localize(parsed_date)
        else:
            parsed_date = parsed_date.astimezone(tz_sp)
        return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
    except Exception:
        pass  

    texto_para_parse = texto_data.replace('às', ' ')
    parsed_date = dateparser.parse(
        texto_para_parse,
        languages=['pt'],
        settings={
            'TIMEZONE': 'America/Sao_Paulo',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
    )

    if not parsed_date:
        raise ValueError(f"Não foi possível interpretar a data: {texto_data}")

    parsed_date = parsed_date.astimezone(tz_sp)
    return parsed_date.strftime("%Y-%m-%dT%H:%M:%S")
