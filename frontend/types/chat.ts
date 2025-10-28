export interface Message {
  id: string
  content: string
  sender: "user" | "ai" | "contact"
  senderName?: string
  timestamp: Date
}

export interface Contact {
  id: string
  name: string
  avatar: string
  status: "online" | "offline" | "away"
  lastMessage: string
  unreadCount: number
  timestamp: string
}
