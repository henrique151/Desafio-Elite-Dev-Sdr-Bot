"use client";

import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Menu, Settings, MessageSquare, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Contact } from "@/types/chat";
import { ContactItem } from "./contact-item";
import { useEffect } from "react";

interface SidebarProps {
  isOpen: boolean;
  onToggle: (forceState?: boolean) => void;
  contacts: Contact[];
  activeContact: Contact;
  onContactSelect: (contact: Contact) => void;
  showBackButton?: boolean;
  onBack?: () => void;
}

export function Sidebar({
  isOpen,
  onToggle,
  contacts,
  activeContact,
  onContactSelect,
  showBackButton = false,
  onBack,
}: SidebarProps) {
  // Toggle automático baseado na largura da tela
  useEffect(() => {
    const handleResize = () => {
      const shouldOpen = window.innerWidth >= 768;
      onToggle(shouldOpen);
    };


    handleResize();

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
 
  }, []); 
 
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape" && isOpen) {
        onToggle(false);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onToggle]);

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border bg-card transition-all duration-300",
        isOpen ? "w-80" : "w-0 overflow-hidden"
      )}
      aria-label="Sidebar de contatos"
      aria-expanded={isOpen}
    >
      <div className="flex h-16 items-center justify-between border-b border-border px-4">
        <h2 className="text-lg font-semibold tracking-tight text-foreground">
          Elite Dev IA
        </h2>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => onToggle(!isOpen)} // toggle manual
          className="lg:hidden"
          aria-label="Abrir/Fechar sidebar"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>

      <div className="border-b border-border p-4">
        {showBackButton && onBack ? (
          <Button
            variant="outline"
            className="w-full justify-start gap-3 border-border bg-transparent"
            onClick={onBack}
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="font-medium">Voltar aos Contatos</span>
          </Button>
        ) : (
          <Button
            variant="default"
            className="w-full justify-start gap-3 bg-primary text-primary-foreground"
          >
            <MessageSquare className="h-5 w-5" />
            <span className="font-medium">Nova Conversa</span>
          </Button>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="space-y-1 p-2">
          {contacts.map((contact) => (
            <ContactItem
              key={contact.id}
              contact={contact}
              isActive={activeContact.id === contact.id}
              onClick={() => onContactSelect(contact)}
            />
          ))}
        </div>
      </ScrollArea>

      <div className="border-t border-border p-4">
        <div className="flex items-center gap-3">
          <Avatar className="h-10 w-10">
            <AvatarImage src="https://api.dicebear.com/9.x/lorelei/svg?seed=Felix" />
            <AvatarFallback className="bg-primary text-primary-foreground">
              VC
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <h3 className="font-semibold text-foreground text-sm">Você</h3>
            <p className="text-muted-foreground text-xs">Online</p>
          </div>
          <Button variant="ghost" size="icon">
            <Settings className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </aside>
  );
}
