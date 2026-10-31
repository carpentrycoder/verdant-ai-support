from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ai_draft import AiDraft, AiDraftStatus
from app.models.message import Message, SenderType


def test_webhook_creates_pending_ai_draft(
    db_session: Session,
    created_webhook: dict,
) -> None:
    message_id = created_webhook["response"]["message_id"]

    draft = db_session.scalar(
        select(AiDraft).where(
            AiDraft.message_id == message_id
        )
    )

    assert draft is not None
    assert draft.status == AiDraftStatus.PENDING
    assert draft.draft_text
    assert draft.approved_text is None
    assert draft.approved_by is None
    assert draft.approved_at is None


def test_pending_drafts_endpoint(
    client: TestClient,
    auth_headers: dict[str, str],
    created_webhook: dict,
) -> None:
    response = client.get(
        "/api/v1/ai-drafts/pending",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["total"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["status"] == "PENDING"


def test_agent_can_approve_ai_draft(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    registered_agent: dict,
    created_webhook: dict,
) -> None:
    customer_message_id = (
        created_webhook["response"]["message_id"]
    )

    draft = db_session.scalar(
        select(AiDraft).where(
            AiDraft.message_id == customer_message_id
        )
    )

    assert draft is not None

    draft_id = draft.id

    approved_text = (
        "Returns are accepted within 7 days of delivery. "
        "Please share your order number for further assistance."
    )

    response = client.post(
        f"/api/v1/ai-drafts/{draft_id}/approve",
        json={
            "approved_text": approved_text,
        },
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["draft"]["status"] == "USED"
    assert body["draft"]["approved_text"] == approved_text
    assert body["draft"]["approved_by"] == (
        registered_agent["agent"]["id"]
    )
    assert body["draft"]["approved_at"] is not None

    assert body["agent_message"]["sender_type"] == "AGENT"
    assert body["agent_message"]["text"] == approved_text

    db_session.expire_all()

    updated_draft = db_session.get(
        AiDraft,
        draft_id,
    )

    assert updated_draft is not None
    assert updated_draft.status == AiDraftStatus.USED
    assert updated_draft.approved_text == approved_text

    agent_message = db_session.scalar(
        select(Message).where(
            Message.id == body["agent_message"]["id"]
        )
    )

    assert agent_message is not None
    assert agent_message.sender_type == SenderType.AGENT
    assert agent_message.text == approved_text


def test_ai_draft_cannot_be_approved_twice(
    client: TestClient,
    db_session: Session,
    auth_headers: dict[str, str],
    created_webhook: dict,
) -> None:
    customer_message_id = (
        created_webhook["response"]["message_id"]
    )

    draft = db_session.scalar(
        select(AiDraft).where(
            AiDraft.message_id == customer_message_id
        )
    )

    assert draft is not None

    endpoint = (
        f"/api/v1/ai-drafts/{draft.id}/approve"
    )

    payload = {
        "approved_text": "Approved final response.",
    }

    first_response = client.post(
        endpoint,
        json=payload,
        headers=auth_headers,
    )

    second_response = client.post(
        endpoint,
        json=payload,
        headers=auth_headers,
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "AI draft has already been used or cannot be approved"
    )


def test_ai_draft_approval_requires_authentication(
    client: TestClient,
    db_session: Session,
    created_webhook: dict,
) -> None:
    customer_message_id = (
        created_webhook["response"]["message_id"]
    )

    draft = db_session.scalar(
        select(AiDraft).where(
            AiDraft.message_id == customer_message_id
        )
    )

    assert draft is not None

    response = client.post(
        f"/api/v1/ai-drafts/{draft.id}/approve",
        json={
            "approved_text": "Unauthorized response attempt.",
        },
    )

    assert response.status_code == 401