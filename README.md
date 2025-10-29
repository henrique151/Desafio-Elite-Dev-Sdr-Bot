Perfeito! Aqui está uma versão completa, organizada e profissional do README para o seu projeto **SDR-Agendamento**, incorporando **dificuldades, soluções, instalação, setup e notas de deploy**.

---

# SDR-Agendamento

Sistema de agendamento de reuniões automatizado, integrando Google Calendar, Pipefy e uma API de Inteligência Artificial (Gemini), com backend em **FastAPI** e frontend em **Next.js** com TypeScript e TailwindCSS.

---

## 📝 Descrição do Projeto

O SDR-Agendamento permite que leads agendem reuniões automaticamente, sugere horários disponíveis e integra informações diretamente ao **Pipefy** para gestão de vendas. Ele combina:

* Agendamento automático no **Google Calendar**.
* Geração de links de reunião via Google Meet.
* Integração com **Pipefy** para registrar leads e atualizar cards.
* Respostas automáticas com IA (Gemini API).
* Frontend interativo com **Next.js + TailwindCSS**.

---

## ⚠️ Dificuldades Encontradas

Durante o desenvolvimento, enfrentamos desafios que impactaram a implementação completa:

### 1. Escolha da API de Inteligência Artificial

* **Problema:** OpenAI é paga e não havia orçamento disponível.
* **Solução adotada:** Gemini API, mas apresentou instabilidade (requisições lentas, sobrecarga e quedas).
* **Impacto:** Funcionalidade de AI limitada e menos confiável.

### 2. Deploy do Webchat

* Backend em **FastAPI** e frontend em **Next.js** exigem deploy separado:

  * Backend em Render.
  * Frontend em Vercel.
* Problemas de comunicação entre backend e frontend impediram o deploy completo.

### 3. Plataforma de Agendamento

* Inicialmente foi testada **Calendly**, mas não permitia gerar links automáticos.
* Migração para **Google Calendar**, porém:

  * Tentativa de usar Service Account com **Domain-Wide Delegation** falhou.
  * Convites para emails externos não foram possíveis devido a restrições de autenticação.
* Impacto: Automação completa de agendamento e envio de convites limitada.

### 4. Testes Locais vs. Produção

* Backend funcionava localmente, mas ao realizar deploy, falhou por erros de autenticação e comunicação com frontend.

### 5. O que ainda falta

* Resolver autenticação do Google Calendar para convites automáticos a emails externos.
* Melhorar estabilidade do uso da Gemini API ou substituir por alternativa confiável.
* Implementar deploy unificado para comunicação confiável entre frontend e backend.
* Testar ferramentas alternativas de agendamento (ex: **Cal.com**).

---

## ⚙️ Instalação e Configuração do Projeto

### 1. Clone o repositório

```bash
git clone <URL_DO_REPOSITORIO>
cd sdr-elite-dev-ia/backend
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do backend com:

```env
GOOGLE_CALENDAR_ID="SEU_CALENDAR_ID"
GOOGLE_CLIENT_ID="SEU_CLIENT_ID"
GOOGLE_CLIENT_SECRET="SEU_CLIENT_SECRET"
GOOGLE_OAUTH_TOKEN="app/credentials/token.pkl"
PIPEFY_ACCESS_TOKEN="SEU_PIPEFY_ACCESS_TOKEN"
PIPEFY_PRE_SALES_PIPE_ID="SEU_PIPEFY_PIPE_ID"
GEMINI_API_KEY="SUA_CHAVE_GEMINI"
FRONTEND_URL="http://localhost:3000"
```

### 5. Gerar token OAuth do Google Calendar

1. Coloque o arquivo `credentials.json` do Google na pasta `app/credentials/`.
2. Execute o script de autenticação para gerar `token.pkl`:

```bash
python -m app.services.calendar_service
```

3. Siga as instruções no navegador para autenticar a conta Google.

### 6. Rodar o backend

```bash
uvicorn app.main:app --reload
```

### 7. Rodar o frontend

```bash
cd ../frontend
npm install
npm run dev
```

* Acesse `http://localhost:3000` para testar o frontend.

---

## 🔗 Fluxo de Funcionamento

1. Usuário escolhe horário para reunião.
2. Backend verifica disponibilidade no Google Calendar.
3. Se disponível:

   * Cria evento no Google Calendar.
   * Envia link da reunião via Pipefy e registra lead.
4. Se ocupado:

   * Sugere horários alternativos.
   * Permite nova tentativa de agendamento.

---

## 📌 Observações

* Funcionalidade completa de envio de convites automáticos para emails externos depende de ajustes na autenticação do Google Calendar.
* A versão de produção precisa de comunicação entre Render (backend) e Vercel (frontend) para funcionar corretamente.
* Instabilidade da Gemini API pode impactar respostas de AI.

---


