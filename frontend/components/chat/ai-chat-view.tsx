"use client";

import { useState, useEffect, useRef } from "react";
import type { Message } from "@/types/chat";
import { Sidebar } from "./sidebar";
import { ChatHeader } from "./chat-header";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { ChatFooter } from "./footer";
import { sendMessageToAPI } from "@/services/api";
import { supabase } from "@/lib/supabase";

interface AIChatViewProps {
  onBack: () => void;
}

const SESSION_TIMEOUT = 1000 * 60 * 20;

export function AIChatView({ onBack }: AIChatViewProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const maxRetries = 3;

  useEffect(() => {
    if (typeof window === "undefined") return;

    let id = localStorage.getItem("session_id");
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem("session_id", id);
    }
    setSessionId(id);
  }, []);

  useEffect(() => {
    if (!sessionId) return;

    const savedTime = localStorage.getItem(`chat_${sessionId}_time`);
    const now = Date.now();

    if (!savedTime || now - Number(savedTime) > SESSION_TIMEOUT) {
      localStorage.removeItem(`chat_${sessionId}`);
      supabase.from("messages").delete().eq("session_id", sessionId);
    }

    localStorage.setItem(`chat_${sessionId}_time`, now.toString());
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;

    const loadMessages = async () => {
      const { data } = await supabase
        .from("messages")
        .select("*")
        .eq("session_id", sessionId)
        .order("timestamp", { ascending: true });

      if (data && data.length > 0) {
        setMessages(
          data.map((m: any) => ({
            id: m.id.toString(),
            sender: m.sender,
            content: m.content,
            timestamp: new Date(m.timestamp),
          }))
        );
      } else {
        const welcome: Message = {
          id: "ai-welcome",
          sender: "ai",
          content:
            "Olá! Sou o Agente SDR da Elite Dev, um assistente de pré-vendas dedicado a entender suas necessidades e ajudar você a encontrar a melhor solução para sua empresa!",
          timestamp: new Date(),
        };
        setMessages([welcome]);
        await supabase.from("messages").insert([
          {
            session_id: sessionId,
            sender: "ai",
            content: welcome.content,
            timestamp: new Date(),
          },
        ]);
      }
    };

    loadMessages();
  }, [sessionId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    if (!sessionId || loading || !content.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    await supabase.from("messages").insert([
      {
        session_id: sessionId,
        sender: "user",
        content,
        timestamp: userMessage.timestamp,
      },
    ]);

    let attempts = 0;
    let success = false;

    while (!success && attempts < maxRetries) {
      attempts++;
      try {
        const history = [...messages, userMessage].map((m) => ({
          role: m.sender === "ai" ? "model" : "user",
          parts: [{ text: m.content }],
        }));

        const res = await sendMessageToAPI(content, sessionId, history);

        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          sender: "ai",
          content: "",
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, aiMessage]);

        const { data: inserted } = await supabase
          .from("messages")
          .insert([
            {
              session_id: sessionId,
              sender: "ai",
              content: "",
              timestamp: aiMessage.timestamp,
            },
          ])
          .select("id")
          .single();

        const dbMessageId = inserted?.id;

        let currentText = "";
        for (let i = 0; i < res.response.length; i++) {
          currentText += res.response[i];
          setMessages((prev) =>
            prev.map((m) =>
              m.id === aiMessage.id ? { ...m, content: currentText } : m
            )
          );

          if (dbMessageId) {
            await supabase
              .from("messages")
              .update({ content: currentText })
              .eq("id", dbMessageId);
          }

          await new Promise((r) => setTimeout(r, 3));
        }

        success = true;
      } catch (err) {
        console.error(err);
      }
    }

    setLoading(false);
  };

  // 🔹 Evita renderização antes de carregar sessionId
  if (!sessionId) return null;

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        contacts={[]}
        activeContact={{} as any}
        onContactSelect={() => {}}
        showBackButton
        onBack={onBack}
      />

      <div className="flex-1 flex flex-col overflow-hidden">
        <ChatHeader
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          showAIButton={false}
          showBackButton
          onBack={onBack}
          isAIChat
        />

        <MessageList messages={messages} isAIChat />

        <MessageInput
          onSend={handleSendMessage}
          placeholder="Pergunte qualquer coisa para a IA..."
          isAIChat
          disabled={loading}
        />

        <ChatFooter />
      </div>
    </div>
  );
}
