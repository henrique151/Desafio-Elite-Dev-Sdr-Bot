"use client"

import { useState } from "react"
import { AIChatView } from "./chat/ai-chat-view"
import { ContactsChatView } from "./chat/contacts-chat-view"

export function WebChat() {
  const [showAIChat, setShowAIChat] = useState(false)

  if (showAIChat) {
    return <AIChatView onBack={() => setShowAIChat(false)} />
  }

  return <ContactsChatView onAIClick={() => setShowAIChat(true)} />
}
