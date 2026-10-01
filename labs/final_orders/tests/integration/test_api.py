def register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secreto123",
        },
    )

    assert response.status_code == 201


def login_user(client) -> str:
    response = client.post(
        "/auth/login",
        data={
            "username": "alice",
            "password": "secreto123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
    }


def test_create_and_list_orders(client):
    register_user(client)
    token = login_user(client)
    headers = auth_headers(token)

    create_response = client.post(
        "/orders/",
        headers=headers,
        json={
            "items": [
                {
                    "product_name": "Keyboard",
                    "quantity": 2,
                    "unit_price": "50.00",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    created = create_response.json()

    assert created["user_id"] > 0
    assert created["total"] == "100.00"
    assert created["status"] == "PENDING"

    list_response = client.get(
        "/orders/",
        headers=headers,
    )

    assert list_response.status_code == 200

    orders = list_response.json()

    assert len(orders) == 1
    assert orders[0]["id"] == created["id"]


def test_orders_require_authentication(client):
    response = client.get("/orders/")

    assert response.status_code == 401
