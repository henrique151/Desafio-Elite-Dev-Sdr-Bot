"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { Contact } from "@/types/chat"

interface ContactItemProps {
  contact: Contact
  isActive: boolean
  onClick: () => void
}

export function ContactItem({ contact, isActive, onClick }: ContactItemProps) {
  const getStatusColor = (status: Contact["status"]) => {
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
    <button
      onClick={onClick}
      className={cn(
        "flex w-full items-center gap-3 rounded-lg p-3 text-left transition-colors hover:bg-secondary/50",
        isActive && "bg-secondary",
      )}
    >
      <div className="relative">
        <Avatar className="h-12 w-12">
          <AvatarImage src={contact.avatar || "/placeholder.svg"} />
          <AvatarFallback className="bg-primary text-primary-foreground">
            {contact.name
              .split(" ")
              .map((n) => n[0])
              .join("")}
          </AvatarFallback>
        </Avatar>
        <span
          className={cn(
            "absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-card",
            getStatusColor(contact.status),
          )}
        />
      </div>
      <div className="flex-1 overflow-hidden">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-foreground text-sm">{contact.name}</h3>
          <span className="text-muted-foreground text-xs">{contact.timestamp}</span>
        </div>
        <p className="truncate text-muted-foreground text-sm">{contact.lastMessage}</p>
      </div>
      {contact.unreadCount > 0 && (
        <Badge className="h-5 min-w-5 rounded-full bg-primary px-1.5 text-primary-foreground text-xs">
          {contact.unreadCount}
        </Badge>
      )}
    </button>
  )
}
