export function ChatFooter() {
  return (
    <footer className="border-t border-border/40 bg-background/95 px-6 py-3 backdrop-blur-sm">
      <div className="flex items-center justify-between text-xs text-muted-foreground">
        <p>© 2025 WebChat Dark. Todos os direitos reservados.</p>
        <div className="flex gap-4">
          <button className="transition-colors hover:text-foreground">Privacidade</button>
          <button className="transition-colors hover:text-foreground">Termos</button>
          <button className="transition-colors hover:text-foreground">Suporte</button>
        </div>
      </div>
    </footer>
  )
}
