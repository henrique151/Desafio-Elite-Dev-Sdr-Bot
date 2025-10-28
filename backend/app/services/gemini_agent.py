import logging
import time
import pytz
from datetime import datetime
from typing import List, Dict, Any
from fastapi import HTTPException
from google import genai
from google.genai import types
from google.genai.errors import APIError

from .pipefy_service import registrar_lead, atualizar_card_com_reuniao
from .calendar_service import oferecer_horarios, agendar_reuniao

# ============================
# Configuração do Logger
# ============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================
# Inicialização do Cliente Gemini
# ============================
try:
    client = genai.Client()
    logger.info("Cliente Gemini inicializado com sucesso.")
except Exception as e:
    logger.error(
        f"Erro ao inicializar o cliente Gemini. Verifique GEMINI_API_KEY: {e}")
    client = None

# ============================
# Ferramentas disponíveis
# ============================
AVAILABLE_TOOLS = {
    "registrar_lead": registrar_lead,
    "atualizar_card_com_reuniao": atualizar_card_com_reuniao,
    "oferecer_horarios": oferecer_horarios,
    "agendar_reuniao": agendar_reuniao,
}

# ============================
# Instrução do Sistema do Agente SDR
# ============================
SDR_SYSTEM_INSTRUCTION = """
Você é o **Agente SDR-Elite-Dev-IA**, um assistente de pré-vendas profissional, empático e eficiente, que conduz conversas com naturalidade e clareza.

**Seu objetivo principal:**
Qualificar leads e agendar reuniões com o time comercial, usando as ferramentas disponíveis.

---

### Fluxo ideal de conversa

1. **Apresentação natural**
   - Cumprimente o cliente de forma breve e simpática.
   - Diga em uma frase o motivo do contato (ex: “sou da equipe da Elite Dev e quero entender melhor suas necessidades para te ajudar no projeto”).

2. **Descoberta progressiva**
   - Faça perguntas abertas e naturais, uma de cada vez:
     - Nome
     - Empresa
     - E-mail
     - Necessidade/dor
   - Sempre contextualize a pergunta (ex: “Para que eu possa te ajudar melhor, você pode me dizer o nome da sua empresa?”).

3. **Confirmação de interesse**
   - Resuma o que foi entendido (“Entendi, você busca X para resolver Y”).
   - Pergunte se o cliente gostaria de conversar com o time técnico/comercial.
   - **Só agende se o cliente confirmar claramente.**

4. **Agendamento**
   - Sempre use o fuso horário fixo: "America/Sao_Paulo"
   - Use `oferecer_horarios` para sugerir 2-3 opções.
   - Após o cliente escolher, chame `agendar_reuniao`.
   - Informe a data, hora e link da reunião de forma clara e agradável.

5. **Registro**
   - Registre o lead no Pipefy usando `registrar_lead`.
   - Se o e-mail já existir, atualize o card existente.
   - Se o cliente não quiser prosseguir, registre e encerre cordialmente.

---

### Estilo de comunicação
- Tom profissional, leve e empático.
- Faça resumos curtos após blocos de informação (“Perfeito, então você é da empresa X e busca Y, certo?”).
- Evite jargões técnicos.
- Use frases curtas e diretas.
- Nunca repita informações que o cliente já deu.
- Sempre mantenha um tom de **conversa natural**, como se fosse um humano conversando por WhatsApp.
- Para sugerir horários, use o seguinte modelo:
  "Nome do Usuário, temos os seguintes horários disponíveis hoje: 14:00, 15:00 e 16:00 (horário de São Paulo). Qual deles é mais conveniente para você?"

---

### Regras técnicas
- Use as ferramentas disponíveis apenas quando necessário:
  - `registrar_lead(nome, email, empresa, necessidade)`
  - `oferecer_horarios()`
  - `agendar_reuniao(card_id, nome, email, datetime)`
  - `atualizar_card_com_reuniao(card_id, link, data)`
- Sempre use o fuso `"America/Sao_Paulo"`.
- Não gere texto junto com a execução de ferramenta — apenas a chamada.
- Quando retornar ao cliente após usar uma ferramenta, **resuma o que foi feito** (“Perfeito! Reunião agendada para terça às 15h. O link foi enviado para seu e-mail.”).
- Não pergunte fuso horário; use sempre "America/Sao_Paulo".
- Sempre enviar o link da reunião pelo chat com usuário.

### Exemplo de conversa natural
**Agente:** Olá! Sou da Elite Dev, tudo bem? 😊  
Estamos ajudando empresas a acelerar seus projetos de software.  
Você pode me dizer seu nome completo, por favor?

**Cliente:** João Oliveira.

**Agente:** Ótimo, João! E de qual empresa você fala?

**Cliente:** TechPro.

**Agente:** Perfeito, João da TechPro! Qual é o principal desafio que vocês estão enfrentando hoje com tecnologia?

**(segue até coletar informações e agendar reunião)**
"""

# ============================
# Funções auxiliares
# ============================


def prepare_history_for_gemini(history: list[dict]) -> list[dict]:
    prepared = []
    for item in history:
        role = item.get("role", "user")
        if role not in ("user", "model"):
            role = "model"

        parts = []
        for part in item.get("parts", []):
            if "text" in part and part["text"]:
                parts.append({"text": part["text"]})
            elif "functionCall" in part:
                parts.append({"functionCall": part["functionCall"]})
            elif "functionResponse" in part:
                parts.append({"functionResponse": part["functionResponse"]})
        prepared.append({"role": role, "parts": parts})
    return prepared


# ============================
# Execução principal
# ============================
MAX_RETRIES = 3
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"


def run_gemini_agent(history: List[Dict[str, Any]]) -> types.GenerateContentResponse:
    if client is None:
        raise Exception("Cliente Gemini não configurado.")

    tz = pytz.timezone("America/Sao_Paulo")
    hoje = datetime.now(tz).strftime("%d/%m/%Y %H:%M")

    system_instruction_with_date = f"""
        Hoje é {hoje} (fuso horário America/Sao_Paulo).
        Sempre use essa data e hora como referência para determinar se uma reunião está no passado ou no futuro.
        Sempre responda em texto puro, sem Markdown, negrito, itálico ou qualquer outro tipo de formatação.
        Não mencione que o link da reunião foi enviado pelo Gmail.
        {SDR_SYSTEM_INSTRUCTION}
    """
    history = prepare_history_for_gemini(history)
    gemini_contents: List[types.Content] = []

    for item in history:
        role = item["role"]
        parts_data = item["parts"]
        gemini_parts: List[types.Part] = []

        for part in parts_data:
            if "text" in part:
                gemini_parts.append(types.Part(text=part["text"]))
            elif "functionCall" in part:
                fc = part["functionCall"]
                gemini_parts.append(types.Part.from_function_call(
                    types.FunctionCall(name=fc["name"], args=fc["args"])
                ))
            elif "functionResponse" in part:
                fr = part["functionResponse"]
                gemini_parts.append(types.Part.from_function_response(
                    name=fr["name"], response=fr["response"]
                ))
        gemini_contents.append(types.Content(role=role, parts=gemini_parts))

    def _call_gemini_with_retry(contents):
        for attempt in range(MAX_RETRIES):
            try:
                return client.models.generate_content(
                    model=PRIMARY_MODEL,
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction_with_date,
                        tools=list(AVAILABLE_TOOLS.values()),
                    ),
                )
            except APIError as e:
                if "503" in str(e) or "UNAVAILABLE" in str(e):
                    wait = 40
                    logger.warning(
                        f"[WARN] Gemini sobrecarregado. Tentativa {attempt+1}/{MAX_RETRIES} — aguardando {wait:.1f}s...")
                    time.sleep(wait)
                elif "NOT_FOUND" in str(e):
                    logger.warning(
                        f"[WARN] Modelo {PRIMARY_MODEL} indisponível. Alternando para {FALLBACK_MODEL}.")
                    return client.models.generate_content(
                        model=FALLBACK_MODEL,
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction_with_date,
                            tools=list(AVAILABLE_TOOLS.values()),
                        ),
                    )
                else:
                    raise
        raise HTTPException(
            status_code=503, detail="O modelo está temporariamente indisponível. Tente novamente em alguns segundos.")

    try:
        response = _call_gemini_with_retry(gemini_contents)

        if hasattr(response, "function_calls") and response.function_calls:
            fc = response.function_calls[0]
            tool_name = fc.name
            args = fc.args or {}

            logger.info(f"[GEMINI] Chamando ferramenta: {tool_name}({args})")

            if tool_name in AVAILABLE_TOOLS:
                tool_func = AVAILABLE_TOOLS[tool_name]
                result = tool_func(**args)

                response = _call_gemini_with_retry([
                    *gemini_contents,
                    types.Content(
                        role="function",
                        parts=[
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"name": tool_name,
                                          "response": result},
                            )
                        ],
                    ),
                ])
            else:
                raise Exception(f"Ferramenta desconhecida: {tool_name}")

        return response

    except Exception as e:
        logger.error(f"Erro no Gemini Agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))
