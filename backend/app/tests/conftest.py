import hashlib
import hmac
import json
import os
from collections.abc import Generator
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.db import get_db
from app.main import app
from app.services.ai_service import GeneratedDraft


# ---------------------------------------------------------
# Environment
# ---------------------------------------------------------

load_dotenv()


TEST_DB_URL = os.getenv("TEST_DB_URL")


if not TEST_DB_URL:
    raise RuntimeError(
        "TEST_DB_URL is missing. Add a dedicated test database "
        "or dedicated Neon test branch URL to your .env file."
    )


# ---------------------------------------------------------
# Test Database Safety Checks
# ---------------------------------------------------------

test_url = make_url(TEST_DB_URL)
development_url = make_url(settings.DB_URL)


# Exact same URL is never allowed.
if TEST_DB_URL == settings.DB_URL:
    raise RuntimeError(
        "Safety check failed: TEST_DB_URL cannot be the same "
        "as DB_URL."
    )


# For Neon, separate branches can use the same database name
# (for example 'neondb') but will have different hosts.
#
# If both host and database name match, assume that this is
# the same database and stop immediately.
if (
    test_url.host == development_url.host
    and test_url.database == development_url.database
):
    raise RuntimeError(
        "Safety check failed: TEST_DB_URL appears to point "
        "to the same database host and database as DB_URL."
    )


# ---------------------------------------------------------
# Test Database Engine
# ---------------------------------------------------------

test_engine = create_engine(
    TEST_DB_URL,
    pool_pre_ping=True,
)


TestingSessionLocal = sessionmaker(
    bind=test_engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


# ---------------------------------------------------------
# Database Reset
# ---------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_test_database() -> Generator[None, None, None]:
    """
    Reset the dedicated test database before every test.

    IMPORTANT:
    TEST_DB_URL must point to a dedicated test database
    or dedicated Neon test branch.

    Never use the development database here.
    """

    Base.metadata.drop_all(
        bind=test_engine,
    )

    Base.metadata.create_all(
        bind=test_engine,
    )

    yield

    Base.metadata.drop_all(
        bind=test_engine,
    )


# ---------------------------------------------------------
# Direct DB Session
# ---------------------------------------------------------

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db

    finally:
        db.close()


# ---------------------------------------------------------
# FastAPI Test Client
# ---------------------------------------------------------

@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """
    FastAPI TestClient configured with:

    - dedicated test database
    - deterministic AI generation
    - test DB health check
    """

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()

        try:
            yield db

        finally:
            db.close()

    def fake_generate_ai_draft(
        customer_message: str,
    ) -> GeneratedDraft:
        """
        Prevent real Groq API calls during tests.
        """

        return GeneratedDraft(
            text=(
                "This is a deterministic test AI response "
                f"for: {customer_message}"
            ),
            knowledge_context=(
                "Test knowledge-base context"
            ),
            generated_by_ai=True,
        )

    # Override production DB dependency.
    app.dependency_overrides[get_db] = override_get_db

    # webhook_service imports generate_ai_draft directly.
    # Therefore patch the symbol where it is used.
    monkeypatch.setattr(
        "app.services.webhook_service.generate_ai_draft",
        fake_generate_ai_draft,
    )

    # /health/db uses app.main.engine.
    # Redirect it to the test engine.
    monkeypatch.setattr(
        "app.main.engine",
        test_engine,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# Agent Fixtures
# ---------------------------------------------------------

@pytest.fixture
def unique_agent_payload() -> dict[str, str]:
    unique_value = uuid4().hex

    return {
        "name": "Test Agent",
        "email": (
            f"agent-{unique_value}@example.com"
        ),
        "password": "StrongTestPassword123!",
    }


@pytest.fixture
def registered_agent(
    client: TestClient,
    unique_agent_payload: dict[str, str],
) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json=unique_agent_payload,
    )

    assert response.status_code == 201

    return {
        "credentials": unique_agent_payload,
        "agent": response.json(),
    }


@pytest.fixture
def auth_token(
    client: TestClient,
    registered_agent: dict,
) -> str:
    credentials = registered_agent[
        "credentials"
    ]

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": credentials["email"],
            "password": credentials["password"],
        },
    )

    assert response.status_code == 200

    return response.json()[
        "access_token"
    ]


@pytest.fixture
def auth_headers(
    auth_token: str,
) -> dict[str, str]:
    return {
        "Authorization": (
            f"Bearer {auth_token}"
        ),
    }


# ---------------------------------------------------------
# Webhook HMAC Helpers
# ---------------------------------------------------------

def create_webhook_signature(
    raw_body: bytes,
) -> str:
    """
    Create the same HMAC-SHA256 signature expected
    by the webhook endpoint.
    """

    digest = hmac.new(
        key=settings.WEBHOOK_SECRET.encode(
            "utf-8"
        ),
        msg=raw_body,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return f"sha256={digest}"


def send_signed_webhook(
    client: TestClient,
    payload: dict,
):
    """
    Serialize, sign and send the exact same byte sequence.

    This ensures HMAC verification uses exactly
    the request body that is transmitted.
    """

    raw_body = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode("utf-8")

    signature = create_webhook_signature(
        raw_body=raw_body,
    )

    return client.post(
        "/api/v1/webhook",
        content=raw_body,
        headers={
            "Content-Type": (
                "application/json"
            ),
            "X-Webhook-Signature": (
                signature
            ),
        },
    )


@pytest.fixture
def webhook_sender(
    client: TestClient,
):
    def sender(
        payload: dict,
    ):
        return send_signed_webhook(
            client=client,
            payload=payload,
        )

    return sender


# ---------------------------------------------------------
# Webhook Test Payload
# ---------------------------------------------------------

@pytest.fixture
def customer_webhook_payload() -> dict:
    unique_value = uuid4().hex

    return {
        "event_id": (
            f"evt_{unique_value}"
        ),
        "customer": {
            "id": (
                f"cust_{unique_value}"
            ),
            "name": "Test Customer",
            "phone": "+919876543210",
        },
        "message": {
            "id": (
                f"msg_{unique_value}"
            ),
            "text": (
                "What is your return policy?"
            ),
        },
    }


# ---------------------------------------------------------
# Pre-created Webhook Fixture
# ---------------------------------------------------------

@pytest.fixture
def created_webhook(
    webhook_sender,
    customer_webhook_payload: dict,
) -> dict:
    response = webhook_sender(
        customer_webhook_payload
    )

    assert response.status_code == 200

    response_body = response.json()

    assert (
        response_body["duplicate"]
        is False
    )

    return {
        "payload": (
            customer_webhook_payload
        ),
        "response": (
            response_body
        ),
    }