"use client";

import { useEffect, useRef, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { cn } from "@/lib/utils";
import type { Message, Contact } from "@/types/chat";

interface MessageListProps {
  messages: Message[];
  activeContact?: Contact;
  isAIChat?: boolean;
}

export function MessageList({
  messages,
  activeContact,
  isAIChat = false,
}: MessageListProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isClient, setIsClient] = useState(false);

  // ✅ Marca que está rodando no cliente (corrige hydration error)
  useEffect(() => {
    setIsClient(true);
  }, []);

  // ✅ Faz scroll suave até o final sempre que novas mensagens chegam
  useEffect(() => {
    const el = scrollRef.current;
    if (el) {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    }
  }, [messages]);

  return (
    <div className="flex-1 h-0 bg-background/50">
      <ScrollArea className="h-full px-6 py-6">
        {/* 🔹 Ref movido para container interno, não no Viewport */}
        <div
          ref={scrollRef}
          className="mx-auto max-w-4xl space-y-4"
          role="log"
          aria-live="polite"
        >
          {messages.map((message) => {
            const isLoadingMessage = message.id === "ai-loading";
            const isUser = message.sender === "user";
            const isAI = message.sender === "ai";

            return (
              <div
                key={message.id}
                className={cn(
                  "flex gap-3",
                  isUser ? "justify-end" : "justify-start"
                )}
              >
                {!isUser && (
                  <Avatar
                    className={cn("h-9 w-9", isAI && "border-2 border-accent")}
                  >
                    <AvatarImage
                      src={isAI ? "/ai-bot.jpg" : activeContact?.avatar}
                    />
                    <AvatarFallback
                      className={cn(
                        "text-xs",
                        isAI
                          ? "bg-accent text-accent-foreground"
                          : "bg-primary text-primary-foreground"
                      )}
                    >
                      {isAI
                        ? "AI"
                        : activeContact?.name
                            ?.split(" ")
                            .map((n) => n[0])
                            .join("")}
                    </AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={cn(
                    "max-w-[70%] rounded-2xl px-4 py-3 shadow-sm break-words",
                    isUser
                      ? "bg-primary text-primary-foreground"
                      : isAI
                      ? "bg-gradient-to-br from-accent/20 to-accent/10 text-foreground border border-accent/30"
                      : "bg-secondary text-secondary-foreground",
                    isLoadingMessage && "italic opacity-80"
                  )}
                >
                  {isLoadingMessage ? (
                    <div className="flex gap-1">
                      <span className="animate-pulse">.</span>
                      <span className="animate-pulse delay-75">.</span>
                      <span className="animate-pulse delay-150">.</span>
                    </div>
                  ) : (
                    <>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </p>
                      {isClient && (
                        <span className="mt-1.5 block text-xs opacity-60">
                          {message.timestamp.toLocaleTimeString("pt-BR", {
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </span>
                      )}
                    </>
                  )}
                </div>

                {isUser && (
                  <Avatar className="h-9 w-9">
                    <AvatarImage src="https://api.dicebear.com/9.x/lorelei/svg?seed=Felix" />
                    <AvatarFallback className="bg-muted text-muted-foreground text-xs">
                      Vc
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
