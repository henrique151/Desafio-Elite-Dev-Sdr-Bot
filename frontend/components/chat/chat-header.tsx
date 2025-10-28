"use client"

import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Menu, Sparkles, ArrowLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import type { Contact } from "@/types/chat"

interface ChatHeaderProps {
  contact?: Contact
  sidebarOpen: boolean
  onToggleSidebar: () => void
  onAIClick?: () => void
  showAIButton?: boolean
  showBackButton?: boolean
  onBack?: () => void
  isAIChat?: boolean
}

export function ChatHeader({
  contact,
  sidebarOpen,
  onToggleSidebar,
  onAIClick,
  showAIButton = true,
  showBackButton = false,
  onBack,
  isAIChat = false,
}: ChatHeaderProps) {
  const getStatusColor = (status?: Contact["status"]) => {
    if (!status) return "bg-green-500"
    switch (status) {
      case "online":
        return "bg-green-500"
      case "away":
        return "bg-yellow-500"
      case "offline":
        return "bg-gray-500"
    }
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-card px-6">
      <div className="flex items-center gap-3">
        {!sidebarOpen && (
          <Button variant="ghost" size="icon" onClick={onToggleSidebar}>
            <Menu className="h-5 w-5" />
          </Button>
        )}
        <div className="relative">
          <Avatar className={cn("h-10 w-10", isAIChat && "border-2 border-accent")}>
            <AvatarImage src={isAIChat ? "/ai-bot.jpg" : contact?.avatar || "/placeholder.svg"} />
            <AvatarFallback
              className={cn(isAIChat ? "bg-accent text-accent-foreground" : "bg-primary text-primary-foreground")}
            >
              {isAIChat
                ? "AI"
                : contact?.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
            </AvatarFallback>
          </Avatar>
          <span
            className={cn(
              "absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-card",
              getStatusColor(isAIChat ? "online" : contact?.status),
            )}
          />
        </div>
        <div>
          <h1 className="font-semibold text-foreground text-sm">{isAIChat ? "Assistente IA" : contact?.name}</h1>
          <p className="text-muted-foreground text-xs capitalize">{isAIChat ? "Sempre disponível" : contact?.status}</p>
        </div>
      </div>

      {showBackButton && onBack ? (
        <Button variant="outline" onClick={onBack} className="gap-2 border-border bg-transparent">
          <ArrowLeft className="h-4 w-4" />
          Voltar
        </Button>
      ) : showAIButton && onAIClick ? (
        <Button
          size="lg"
          onClick={onAIClick}
          className="group relative overflow-hidden bg-gradient-to-r from-primary to-accent text-primary-foreground shadow-lg shadow-primary/50 transition-all hover:scale-105 hover:shadow-xl hover:shadow-primary/60"
        >
          <Sparkles className="mr-2 h-5 w-5 animate-pulse" />
          <span className="font-semibold">Assistência IA</span>
          <div className="absolute inset-0 -z-10 bg-gradient-to-r from-accent via-primary to-accent opacity-0 blur-xl transition-opacity group-hover:opacity-100" />
        </Button>
      ) : null}
    </header>
  )
}
