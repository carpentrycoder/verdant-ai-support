from fastapi.testclient import TestClient


def test_register_agent(
    client: TestClient,
    unique_agent_payload: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json=unique_agent_payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["name"] == unique_agent_payload["name"]
    assert body["email"] == unique_agent_payload["email"]
    assert body["is_active"] is True
    assert "id" in body

    # Sensitive data must never be returned.
    assert "password" not in body
    assert "password_hash" not in body


def test_duplicate_agent_registration_returns_409(
    client: TestClient,
    unique_agent_payload: dict[str, str],
) -> None:
    first_response = client.post(
        "/api/v1/auth/register",
        json=unique_agent_payload,
    )

    second_response = client.post(
        "/api/v1/auth/register",
        json=unique_agent_payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

    assert second_response.json()["detail"] == (
        "An agent with this email already exists"
    )


def test_agent_login(
    client: TestClient,
    registered_agent: dict,
) -> None:
    credentials = registered_agent["credentials"]

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": credentials["email"],
            "password": credentials["password"],
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["agent"]["email"] == credentials["email"]

    assert "password" not in body["agent"]
    assert "password_hash" not in body["agent"]


def test_login_with_invalid_password_returns_401(
    client: TestClient,
    registered_agent: dict,
) -> None:
    credentials = registered_agent["credentials"]

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": credentials["email"],
            "password": "DefinitelyWrongPassword123!",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_without_token_returns_401(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/auth/me"
    )

    assert response.status_code == 401


def test_auth_me_with_valid_token(
    client: TestClient,
    auth_headers: dict[str, str],
    registered_agent: dict,
) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers,
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == registered_agent["agent"]["id"]
    assert body["email"] == (
        registered_agent["credentials"]["email"]
    )