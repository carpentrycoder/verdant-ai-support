from uuid import uuid4

from fastapi.testclient import TestClient


def test_customer_and_conversation_created_from_webhook(
    client: TestClient,
    auth_headers: dict[str, str],
    created_webhook: dict,
) -> None:
    webhook_response = created_webhook["response"]

    customer_id = webhook_response["customer_id"]
    conversation_id = webhook_response["conversation_id"]

    customer_response = client.get(
        f"/api/v1/customers/{customer_id}",
        headers=auth_headers,
    )

    assert customer_response.status_code == 200

    customer_body = customer_response.json()

    assert customer_body["id"] == customer_id
    assert len(customer_body["conversations"]) == 1

    conversation_response = client.get(
        f"/api/v1/conversations/{conversation_id}",
        headers=auth_headers,
    )

    assert conversation_response.status_code == 200

    conversation_body = conversation_response.json()

    assert conversation_body["status"] == "OPEN"
    assert len(conversation_body["messages"]) == 1
    assert (
        conversation_body["messages"][0]["sender_type"]
        == "CUSTOMER"
    )


def test_same_customer_reuses_open_conversation(
    webhook_sender,
    customer_webhook_payload: dict,
) -> None:
    first_response = webhook_sender(
        customer_webhook_payload
    )

    second_payload = {
        "event_id": f"evt_{uuid4().hex}",
        "customer": customer_webhook_payload["customer"],
        "message": {
            "id": f"msg_{uuid4().hex}",
            "text": "I have another question.",
        },
    }

    second_response = webhook_sender(
        second_payload
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        first_response.json()["conversation_id"]
        == second_response.json()["conversation_id"]
    )

    assert (
        first_response.json()["message_id"]
        != second_response.json()["message_id"]
    )


def test_closed_conversation_causes_new_open_conversation(
    client: TestClient,
    auth_headers: dict[str, str],
    webhook_sender,
    customer_webhook_payload: dict,
) -> None:
    first_response = webhook_sender(
        customer_webhook_payload
    )

    assert first_response.status_code == 200

    first_body = first_response.json()

    old_conversation_id = first_body["conversation_id"]
    customer_id = first_body["customer_id"]

    close_response = client.patch(
        (
            "/api/v1/conversations/"
            f"{old_conversation_id}/status"
        ),
        json={
            "status": "CLOSED",
        },
        headers=auth_headers,
    )

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "CLOSED"

    next_payload = {
        "event_id": f"evt_{uuid4().hex}",
        "customer": customer_webhook_payload["customer"],
        "message": {
            "id": f"msg_{uuid4().hex}",
            "text": "Where is my order?",
        },
    }

    next_response = webhook_sender(
        next_payload
    )

    assert next_response.status_code == 200

    new_conversation_id = (
        next_response.json()["conversation_id"]
    )

    assert new_conversation_id != old_conversation_id

    conversations_response = client.get(
        (
            "/api/v1/customers/"
            f"{customer_id}/conversations"
        ),
        headers=auth_headers,
    )

    assert conversations_response.status_code == 200

    conversations = conversations_response.json()

    assert len(conversations) == 2

    statuses = {
        item["id"]: item["status"]
        for item in conversations
    }

    assert statuses[old_conversation_id] == "CLOSED"
    assert statuses[new_conversation_id] == "OPEN"


def test_conversation_requires_authentication(
    client: TestClient,
    created_webhook: dict,
) -> None:
    conversation_id = (
        created_webhook["response"]["conversation_id"]
    )

    response = client.get(
        f"/api/v1/conversations/{conversation_id}"
    )

    assert response.status_code == 401