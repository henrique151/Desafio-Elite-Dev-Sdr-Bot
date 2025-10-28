const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export interface AgentResponse {
    response: string;
    history: any[];
}

export async function sendMessageToAPI(
    prompt: string,
    sessionId: string,
    history: any[]
): Promise<AgentResponse> {
    const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, session_id: sessionId, history }),
    });

    if (!res.ok) {
        throw new Error(`Erro ao chamar a API: ${res.status}`);
    }

    return res.json();
}
