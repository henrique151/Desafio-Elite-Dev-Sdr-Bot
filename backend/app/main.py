from fastapi import FastAPI, HTTPException
from app.models import AgentRequest, AgentResponse
from app.services.gemini_agent import run_gemini_agent
from app.models import HistoryItem, HistoryPart
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SDR Elite Dev API")

origins = [
    "https://desafio-elite-dev-sdr-bot.vercel.app",
    "desafio-elite-dev-sdr-bot-git-main-henrique151s-projects.vercel.app",
    "https://desafio-elite-dev-sdr-puk1vnj0g-henrique151s-projects.vercel.app",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ===========================
# Endpoint raiz
# ===========================


@app.get("/")
def root():
    return {"message": "API SDR-Elite-Dev-IA rodando 🚀"}

# ===========================
# Endpoint de chat
# ===========================


@app.post("/chat", response_model=AgentResponse)
def chat(request: AgentRequest):
    history = request.history or []
    history.append(
        HistoryItem(
            role="user",
            parts=[HistoryPart(text=request.prompt)]
        )
    )

    try:
        history_for_agent = [
            {"role": h.role, "parts": [{"text": p.text} for p in h.parts]}
            for h in history
        ]

        # executa o Gemini Agent
        response = run_gemini_agent(history_for_agent)

        if hasattr(response, "tool_response") and isinstance(response.tool_response, dict):
            tr = response.tool_response
            if "meeting_link" in tr:
                reply_text = (
                    f"Reunião agendada para {tr.get('meeting_datetime')}.\n"
                    f"Link da reunião: {tr.get('meeting_link')}"
                )
            else:
                reply_text = getattr(response, "text", "Tudo certo!")
        else:
            reply_text = getattr(
                response, "text", "[ERRO] Resposta vazia do Gemini.")

        history.append(
            HistoryItem(
                role="model",
                parts=[HistoryPart(text=reply_text)]
            )
        )

        return AgentResponse(response=reply_text, history=history)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
