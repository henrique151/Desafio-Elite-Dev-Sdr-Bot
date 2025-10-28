"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send } from "lucide-react";

interface MessageInputProps {
  onSend: (message: string) => void;
  placeholder?: string;
  isAIChat?: boolean;
  disabled?: boolean; // ← Adicionei aqui
}

export function MessageInput({
  onSend,
  placeholder = "Digite sua mensagem...",
  isAIChat = false,
  disabled = false, // ← Valor padrão
}: MessageInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    if (!value.trim() || disabled) return;
    onSend(value);
    setValue("");
  };

  return (
    <div className="border-t border-border bg-card p-4">
      <div className="mx-auto max-w-4xl">
        <div className="flex gap-3">
          <Input
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={placeholder}
            className="flex-1 rounded-xl bg-background px-4 py-6 text-sm"
            disabled={disabled}
            role="textbox"
            aria-label="Digite sua mensagem"
            aria-multiline="true"
          />
          <Button
            onClick={handleSend}
            size="icon"
            disabled={disabled}
            className={
              isAIChat
                ? "h-auto w-12 rounded-xl bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 disabled:opacity-50 disabled:cursor-not-allowed"
                : "h-auto w-12 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            }
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
