import { useState, useEffect } from "react";
import type { Message } from "@/types/chat";

export function useChatPersistence(sessionId: string) {
    const [messages, setMessages] = useState<Message[]>(() => {
        if (typeof window === "undefined") return [];
        const saved = localStorage.getItem(`chat_${sessionId}`);
        return saved ? JSON.parse(saved) : [];
    });

    useEffect(() => {
        if (typeof window === "undefined") return;
        localStorage.setItem(`chat_${sessionId}`, JSON.stringify(messages));
    }, [messages, sessionId]);

    return { messages, setMessages };
}
