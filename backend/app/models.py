from pydantic import BaseModel, Field
from typing import List, Optional


class HistoryPart(BaseModel):
    text: Optional[str] = None
    function_call: Optional[dict] = Field(None, alias="functionCall")
    function_response: Optional[dict] = Field(None, alias="functionResponse")

    class Config:

        allow_population_by_field_name = True


class HistoryItem(BaseModel):
    role: str = Field(...,
                      description="O papel na conversa (user, model, tool).")
    parts: List[HistoryPart] = Field(...,
                                     description="O conteúdo da mensagem.")


class AgentRequest(BaseModel):
    prompt: str = Field(..., description="A nova mensagem do usuário.")
    history: Optional[List[HistoryItem]] = Field(
        None, description="Histórico da conversa anterior.")
    session_id: Optional[str] = Field(None, alias="session_id")

    class Config:
        allow_population_by_field_name = True


class AgentResponse(BaseModel):
    response: str = Field(..., description="A resposta de texto do Agente.")
    history: List[HistoryItem] = Field(
        ..., description="Histórico completo e atualizado da conversa.")
