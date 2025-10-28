"use client";

import { useState } from "react";
import type { Contact, Message } from "@/types/chat";
import { Sidebar } from "./sidebar";
import { ChatHeader } from "./chat-header";
import { MessageList } from "./message-list";
import { MessageInput } from "./message-input";
import { ChatFooter } from "./footer";

interface ContactsChatViewProps {
  onAIClick: () => void;
}

const INITIAL_CONTACTS: Contact[] = [
  {
    id: "1",
    name: "Maria Silva",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Maria",
    status: "online",
    lastMessage: "Obrigada pela ajuda!",
    unreadCount: 2,
    timestamp: "10:30",
  },
  {
    id: "2",
    name: "João Santos",
    avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Joao",
    status: "online",
    lastMessage: "Quando podemos conversar?",
    unreadCount: 0,
    timestamp: "09:15",
  },
];

const INITIAL_MESSAGES: Message[] = [
  {
    id: "1",
    content: "Oi! Tudo bem? Preciso de ajuda com um projeto",
    sender: "contact",
    senderName: "Maria Silva",
    timestamp: new Date(Date.now() - 7200000),
  },
  {
    id: "2",
    content:
      "Olá Maria! Claro, estou aqui para ajudar. Pode me contar mais sobre o projeto?",
    sender: "user",
    timestamp: new Date(Date.now() - 7000000),
  },
];

export function ContactsChatView({ onAIClick }: ContactsChatViewProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [contacts] = useState<Contact[]>(INITIAL_CONTACTS);
  const [activeContact, setActiveContact] = useState<Contact>(contacts[0]);
  const [messages, setMessages] = useState<Message[]>(INITIAL_MESSAGES);

  const handleSendMessage = (content: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      content,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);

    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        content:
          "Entendi! Vou processar sua solicitação e retornar com uma resposta detalhada em instantes.",
        sender: "ai",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 1500);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        contacts={contacts}
        activeContact={activeContact}
        onContactSelect={setActiveContact}
      />

      <div className="flex flex-1 flex-col overflow-hidden">
        <ChatHeader
          contact={activeContact}
          sidebarOpen={sidebarOpen}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          onAIClick={onAIClick}
        />

        <MessageList messages={messages} activeContact={activeContact} />

        <MessageInput onSend={handleSendMessage} />

        <ChatFooter />
      </div>
    </div>
  );
}
