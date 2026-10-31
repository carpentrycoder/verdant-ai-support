from fastapi.testclient import TestClient


def test_application_health(
    client: TestClient,
) -> None:
    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    body = response.json()

    assert body["status"] == "ok"
    assert body["service"]


def test_database_health(
    client: TestClient,
) -> None:
    response = client.get(
        "/health/db"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }