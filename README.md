---
# SDR-Agendamento

Sistema de agendamento de reuniões automatizado, integrando **Google Calendar**, **Pipefy** e uma API de Inteligência Artificial (Gemini), com backend em **FastAPI** e frontend em **Next.js** com TypeScript e TailwindCSS.
---

## 📝 Descrição do Projeto

O SDR-Agendamento permite que leads agendem reuniões automaticamente, sugere horários disponíveis e integra informações diretamente ao **Pipefy** para gestão de vendas. Ele combina:

- Agendamento automático no **Google Calendar**.
- Geração de links de reunião via Google Meet.
- Integração com **Pipefy** para registrar leads e atualizar cards.
- Respostas automáticas com IA (Gemini API).
- Frontend interativo com **Next.js + TailwindCSS**.
- Persistência de sessões e transcrições usando **Supabase**.

## ⚙️ Funcionalidades do Projeto

| Funcionalidade                                             | Status          | Descrição                                                                                                      |
| ---------------------------------------------------------- | --------------- | -------------------------------------------------------------------------------------------------------------- |
| Agente conversacional (texto)                              | ✅ Cumprida     | Coleta dados do lead e confirma interesse.                                                                     |
| Sugestão de horários via Google Calendar                   | ✅ Cumprida     | Busca próximos 7 dias e oferece slots disponíveis.                                                             |
| Agendamento automático no Google Calendar                  | ✅ Cumprida     | Cria evento e gera link do Google Meet.                                                                        |
| Registro/atualização de leads no Pipefy                    | ✅ Cumprida     | Cria card ou atualiza card existente.                                                                          |
| Persistência de sessão e transcrição                       | ✅ Cumprida     | Armazena localmente (cookie/localStorage) e em banco de dados via **Supabase**, garantindo histórico completo. |
| Integração com Gemini API                                  | ⚠️ Parcial      | Funcional, mas instável (regras de fallback implementadas).                                                    |
| Deploy frontend/backend                                    | ⚠️ Parcial      | Frontend em Vercel, backend em Render; comunicação precisa ser ajustada para produção.                         |
| Convites automáticos a emails externos via Service Account | ❌ Não cumprida | Google Workspace bloqueia sem Domain-Wide Delegation.                                                          |

---

## ⚠️ Dificuldades Encontradas

Durante o desenvolvimento do SDR-Agendamento, enfrentamos desafios importantes que impactaram a implementação completa e o deploy do projeto:

### 1. Escolha da API de Inteligência Artificial

- **Problema:** A opção inicial seria utilizar a **OpenAI**, mas por questões financeiras, não foi possível usar a API paga.
- **Solução adotada:** Optou-se pela **Gemini API** como alternativa gratuita.
- **Desafios enfrentados:** Durante os testes, as requisições ficavam lentas, sobrecarregadas e, em alguns casos, a API chegava a cair.
- **Impacto:** O uso da IA ficou limitado, instável e menos confiável, afetando a geração de respostas automáticas em tempo real.

### 2. Deploy do Webchat

- **Configuração:** Backend em **FastAPI** (Python) e frontend em **Next.js + TypeScript + TailwindCSS**.
- **Problema:** Para disponibilizar o projeto, foi necessário deploy em duas plataformas distintas:

  - **Backend:** Render
  - **Frontend:** Vercel

- **Desafio:** Problemas de comunicação entre backend e frontend impediram que o projeto funcionasse plenamente em produção.
- **Impacto:** Apesar de funcionar localmente, o deploy completo não foi alcançado.

### 3. Plataforma de Agendamento

- **Testes iniciais:** Utilização do **Calendly**, que não permitia gerar links de reunião de forma automática.
- **Migração:** Passou-se a usar **Google Calendar**.
- **Problema de autenticação:** Tentativa de utilizar **Service Account com Domain-Wide Delegation** falhou, pois contas de serviço **não podem enviar convites para emails externos** sem permissões específicas.
- **Tentativa de solução:** Considerou-se usar **Cal.com**, mas não houve tempo suficiente para implementação.
- **Impacto:** A automação completa de agendamento e envio de convites externos não foi alcançada. A versão local funcionava, mas ao tentar deploy, os mesmos problemas de autenticação impediram o teste remoto.

### 4. Testes Locais vs. Produção

- O backend funcionava corretamente em ambiente local.
- Após mudanças para deploy, surgiram erros de autenticação com o Google Calendar e problemas de comunicação com o frontend.
- **Impacto:** Não foi possível realizar testes de ponta a ponta em produção.

---

## ⚙️ Instalação e Configuração

### 1. Clone o repositório

```bash
git clone https://github.com/henrique151/Desafio-Elite-Dev-Sdr-Bot.git
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

Crie um arquivo `.env` na raiz do backend:

```env
GOOGLE_CALENDAR_ID="SEU_CALENDAR_ID"
GOOGLE_CLIENT_ID="SEU_CLIENT_ID"
GOOGLE_CLIENT_SECRET="SEU_CLIENT_SECRET"
GOOGLE_OAUTH_TOKEN="app/credentials/token.pkl"
PIPEFY_ACCESS_TOKEN="SEU_PIPEFY_ACCESS_TOKEN"
PIPEFY_PRE_SALES_PIPE_ID="SEU_PIPEFY_PIPE_ID"
GEMINI_API_KEY="SUA_CHAVE_GEMINI"
SUPABASE_URL="SUA_URL_SUPABASE"
SUPABASE_KEY="SUA_CHAVE_SUPABASE"
FRONTEND_URL="http://localhost:3000"
```

### 5. Gerar token OAuth do Google Calendar

1. Coloque `credentials.json` do Google na pasta `app/credentials/`.
2. Execute o script de autenticação:

```bash
python -m app.services.calendar_service
```

3. Siga as instruções no navegador para gerar `token.pkl`.

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

Acesse `http://localhost:3000`.

---

## 🔗 Fluxo de Funcionamento

1. Usuário conversa com o agente.
2. Agente coleta dados do lead (nome, email, empresa, dor/necessidade, interesse).
3. Verifica disponibilidade de horários no **Google Calendar**.
4. Se disponível:

   - Agenda reunião automaticamente.
   - Retorna link do Google Meet.
   - Registra ou atualiza lead no **Pipefy**.

5. Se ocupado:

   - Sugere horários alternativos.

6. Sessão e transcrição são armazenadas localmente e no **Supabase**.

---

## 📝 Regras de Negócio

- Critério de gatilho para reunião: **cliente confirma explicitamente interesse**.
- Script sugerido:

  1. Apresentação do agente e do serviço.
  2. Perguntas de descoberta (nome, empresa, necessidade, prazo).
  3. Pergunta direta: "Gostaria de seguir com uma conversa para iniciar o projeto / adquirir o produto?"
  4. Se o cliente confirma:

     - Oferece 2-3 horários disponíveis.
     - Agenda automaticamente.
     - Registra evento e envia link.

  5. Se não confirma, registra no Pipefy e encerra cordialmente.

---

## 💻 Tecnologias Utilizadas

- **Frontend:** Next.js, TypeScript, TailwindCSS, React
- **Backend:** FastAPI, Python
- **Banco de Dados:** Supabase
- **Integrações:** Google Calendar, Google Meet, Pipefy, Gemini API
- **Deploy:** Render (backend), Vercel (frontend)

---

## ✅ Critérios de Sucesso

- Conversa natural com o lead.
- Confirmação explícita de interesse aciona agendamento.
- Evento criado no Google Calendar com link do Meet.
- Leads registrados/atualizados no Pipefy corretamente.
- Histórico de transcrição completo persistido.

---
