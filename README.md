# Verdant AI Support

Verdant AI Support is a full-stack AI-assisted customer-support application built for the Software Engineer, AI & Product Engineering take-home assessment. Customers can send support messages, the backend generates a knowledge-base-grounded AI draft, and authenticated Agents can review, edit and approve the reply before it becomes visible to the customer.

## Live Links

**Frontend:** https://verdant-ai-support-frontend.onrender.com/

**Backend API:** https://verdant-ai-support.onrender.com

**Swagger:** https://verdant-ai-support.onrender.com/docs

**GitHub:** https://github.com/carpentrycoder/verdant-ai-support

**Webhook:** `POST https://verdant-ai-support.onrender.com/api/v1/webhook`

## Repository Structure

```text
verdant-ai-support/
├── backend/     FastAPI, PostgreSQL, Alembic, Groq, Docker, tests
└── frontend/    Next.js, JavaScript, Mantine UI
```

Detailed component documentation:

- `frontend/README.md` - frontend setup, architecture and UI workflow
- `backend/README.md` - backend setup, APIs, AI, webhook and testing

## Tech Stack

### Frontend
- Next.js 16
- React 19
- JavaScript
- Mantine UI
- Tabler Icons

### Backend
- FastAPI
- SQLAlchemy 2
- PostgreSQL / Neon
- Alembic
- Groq `openai/gpt-oss-120b`
- JWT authentication
- HMAC-SHA256 webhook verification
- Docker
- pytest

## End-to-End Flow

```text
Customer
   |
   | sends support message
   v
FastAPI Backend
   |
   | persists Customer / Conversation / Message
   v
Knowledge Base + Groq
   |
   | creates PENDING AI draft
   v
Agent Workspace
   |
   | reviews / edits / approves
   v
USED AI Draft + AGENT Message
   |
   v
Customer sees approved response
```

AI suggestions are never shown directly to customers. Only Agent-approved responses are added to customer-visible conversation history.

## Key Technical Decisions

- **Human-in-the-loop AI:** Groq generates suggestions, but an Agent must approve the final response.
- **Knowledge-base grounding:** AI prompts receive only the relevant support-policy context; fallback responses are available if the provider is unavailable.
- **Webhook security:** external events are signed with HMAC-SHA256 over the exact raw payload.
- **Idempotency:** unique external event/message IDs prevent duplicate webhook retries from creating duplicate customer messages.
- **Conversation lifecycle:** a customer can have historical closed conversations but at most one open conversation at a time.
- **Secret separation:** database, Groq, JWT and webhook secrets remain on the backend. The frontend communicates with the backend through a Next.js server-side proxy.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend `.env.local`:

```env
NEXT_API_URL=https://verdant-ai-support.onrender.com
```

## Validation

Backend:

```bash
pytest -v
```

Frontend:

```bash
npm run lint
npm run build
```

The deployed environment also exposes `GET /api/v1/ai/status` to verify that Groq is configured and reachable without exposing the API key.

## Demo Flow

1. Open the Customer view and send a new support message.
2. Switch to Agent view and sign in.
3. Open the new conversation.
4. Review the generated PENDING AI draft.
5. Edit the suggested reply and approve it.
6. Optionally close the conversation.
7. Return to Customer view and refresh to see the approved Agent response.
8. A reviewer can also call the signed webhook directly and observe the same conversation + AI-draft workflow.

## What I Would Improve Next

- Move AI generation to a background job/queue for lower webhook latency and better retry control.
- Replace the small in-code knowledge base with brand-scoped retrieval backed by a managed search/vector layer.
- Add richer frontend integration tests and end-to-end browser automation.
- Add rate limiting and stronger customer-session controls for the public customer simulator.

## AI Tool Usage

AI assistance was used to accelerate implementation planning, debugging, repetitive scaffolding and test-case generation. Each generated change was validated through compilation, lint/build checks, automated backend tests, API smoke tests, and deployed end-to-end verification. Not every suggestion was correct: examples included framework-version-specific Next.js prerender behavior and environment-specific Docker TLS assumptions, which required direct log-driven debugging and correction.

## Scaling to Multiple Brands

For multiple brands, brand-specific configuration should be separated from core conversation logic: each `brand_id` should map to its own knowledge base, prompt/policy configuration, webhook secret, customer data boundary and branding. Shared infrastructure can continue to serve authentication, conversations, AI orchestration, observability and deployment while keeping retrieval and policies brand-scoped.

## 2 A.M. Failure Scenario

If AI generation fails overnight, customer messages should still be persisted first and remain available to Agents. The system should record the provider failure, use a safe grounded fallback where appropriate, expose the conversation for human handling, and retry asynchronous AI work with bounded retries rather than losing or duplicating customer messages. Alerts should distinguish provider/network failures from database or webhook-authentication failures so the on-call engineer can identify the failing dependency quickly.
