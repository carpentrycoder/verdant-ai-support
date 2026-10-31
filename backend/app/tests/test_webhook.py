import json

from fastapi.testclient import TestClient

from app.tests.conftest import create_webhook_signature


def test_webhook_without_signature_returns_401(
    client: TestClient,
    customer_webhook_payload: dict,
) -> None:
    response = client.post(
        "/api/v1/webhook",
        json=customer_webhook_payload,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Missing webhook signature"
    )


def test_webhook_with_invalid_signature_returns_401(
    client: TestClient,
    customer_webhook_payload: dict,
) -> None:
    response = client.post(
        "/api/v1/webhook",
        json=customer_webhook_payload,
        headers={
            "X-Webhook-Signature": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Invalid webhook signature"
    )


def test_webhook_with_valid_signature_creates_records(
    client: TestClient,
    customer_webhook_payload: dict,
) -> None:
    raw_body = json.dumps(
        customer_webhook_payload,
        separators=(",", ":"),
    ).encode("utf-8")

    signature = create_webhook_signature(
        raw_body=raw_body,
    )

    response = client.post(
        "/api/v1/webhook",
        content=raw_body,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["duplicate"] is False
    assert body["event_id"] == (
        customer_webhook_payload["event_id"]
    )

    assert body["customer_id"] is not None
    assert body["conversation_id"] is not None
    assert body["message_id"] is not None


def test_duplicate_webhook_returns_existing_message(
    webhook_sender,
    customer_webhook_payload: dict,
) -> None:
    first_response = webhook_sender(
        customer_webhook_payload
    )

    second_response = webhook_sender(
        customer_webhook_payload
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    first_body = first_response.json()
    second_body = second_response.json()

    assert first_body["duplicate"] is False
    assert second_body["duplicate"] is True

    assert (
        first_body["conversation_id"]
        == second_body["conversation_id"]
    )

    assert (
        first_body["message_id"]
        == second_body["message_id"]
    )