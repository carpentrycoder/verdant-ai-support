# Verdant AI Support - Backend

FastAPI backend for an AI-assisted customer-support workflow with PostgreSQL persistence, signed webhook ingestion, AI draft generation, and human approval.

## Live Backend

API base:
https://verdant-ai-support.onrender.com

Swagger:
https://verdant-ai-support.onrender.com/docs

AI status endpoint:
`GET /api/v1/ai/status`

Webhook endpoint:
`POST /api/v1/webhook`

## Core Features

- Agent registration, login and JWT authentication
- Argon2 password hashing
- Customers, conversations, messages and AI drafts
- One open conversation per customer
- HMAC-SHA256 webhook validation over the exact raw request body
- `X-Signature: sha256=<hex>` assessment-compatible webhook header
- Webhook idempotency using unique external event/message IDs
- Knowledge-base-grounded AI drafts
- Groq `openai/gpt-oss-120b` integration
- Safe fallback draft when the AI provider is unavailable
- Human review, edit and approval workflow
- PENDING -> USED AI draft lifecycle
- Approved Agent reply persisted in conversation history
- Customer-safe public messaging endpoints
- Docker + Alembic startup migrations
- PostgreSQL on Neon
- Automated backend test suite

## Tech Stack

- Python / FastAPI
- SQLAlchemy 2
- PostgreSQL / Neon
- Alembic
- Pydantic v2
- Psycopg 3
- Groq
- PyJWT
- pwdlib / Argon2
- Docker
- pytest

## Main Environment Variables

```env
DB_URL=postgresql+psycopg://...
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
WEBHOOK_SECRET=...
GROQ_API_KEY=...
GROQ_MODEL=openai/gpt-oss-120b
AI_TEMPERATURE=0.2
AI_MAX_TOKENS=300
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Never commit the real `.env` file.

## Local Setup

```bash
python -m venv .venv
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Swagger is available at `http://127.0.0.1:8000/docs`.

## Tests

```bash
pytest -v
```

Tests use a separate test database / Neon branch and mock the AI generation path where deterministic behavior is required.

## Docker

```bash
docker compose build
docker compose up -d
```

The container runs Alembic migrations before starting Uvicorn.

## Reviewer Webhook Example

The deployed webhook accepts an HMAC-SHA256 signature in `X-Signature`.

```json
{
  "event_id": "evt_example_001",
  "type": "message.received",
  "brand_id": "verdant-co",
  "timestamp": "2026-11-03T10:15:22Z",
  "customer": {
    "id": "cust_example_001",
    "name": "Example Customer",
    "phone": "+919800000001"
  },
  "message": {
    "id": "msg_example_001",
    "type": "text",
    "text": "What is your return policy?"
  }
}
```

The same `event_id` can be retried safely: the backend returns the existing message instead of creating a duplicate.
