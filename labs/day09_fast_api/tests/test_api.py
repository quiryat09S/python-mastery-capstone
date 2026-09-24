from unittest.mock import patch

import pytest


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Orders API funcionando",
    }
    assert "X-Process-Time" in response.headers


def test_register_user(client):
    response = client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secreto123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"
    assert "hashed_password" not in data


def test_register_duplicate_user(client):
    payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "secreto123",
    }

    first_response = client.post(
        "/auth/register",
        json=payload,
    )

    second_response = client.post(
        "/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_login(client):
    client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secreto123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "alice",
            "password": "secreto123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json={
            "username": "alice",
            "email": "alice@example.com",
            "password": "secreto123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "alice",
            "password": "incorrecta",
        },
    )

    assert response.status_code == 401


def test_orders_requires_authentication(client):
    response = client.get("/orders/")

    assert response.status_code == 401


# Función auxiliar para obtener un token
def get_token(client):
    client.post(
        "/auth/register",
        json={
            "username": "orders_user",
            "email": "orders@example.com",
            "password": "secreto123",
        },
    )

    response = client.post(
        "/auth/login",
        data={
            "username": "orders_user",
            "password": "secreto123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


# Prueba antes de implementar Endpoint nuevo
def create_order(client, headers, status="PENDING"):
    response = client.post(
        "/orders/",
        headers=headers,
        json={
            "status": status,
            "items": [
                {
                    "product_name": "Teclado",
                    "quantity": 1,
                    "unit_price": "35.50",
                }
            ],
        },
    )

    assert response.status_code == 201

    return response.json()


# Primer test agregado
def test_cancel_pending_order(client):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    order = create_order(
        client,
        headers,
    )

    response = client.post(
        f"/orders/{order['id']}/cancel",
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == order["id"]
    assert data["status"] == "CANCELLED"


# Pruebas con unittest.mock
def test_cancel_pending_order_sends_notification(client):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    order = create_order(
        client,
        headers,
    )

    with patch(
        "labs.day09_fast_api.routers.orders."
        "send_order_cancelled_notification"
    ) as notification_mock:
        response = client.post(
            f"/orders/{order['id']}/cancel",
            headers=headers,
        )

    assert response.status_code == 200

    notification_mock.assert_called_once_with(
        username="orders_user",
        order_id=order["id"],
    )


def test_cancel_non_pending_order_does_not_notify(client):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    order = create_order(
        client,
        headers,
        status="CONFIRMED",
    )

    with patch(
        "labs.day09_fast_api.routers.orders."
        "send_order_cancelled_notification"
    ) as notification_mock:
        response = client.post(
            f"/orders/{order['id']}/cancel",
            headers=headers,
        )

    assert response.status_code == 409
    notification_mock.assert_not_called()


# Se agrega prueba parametrizada
@pytest.mark.parametrize(
    "initial_status",
    [
        "CONFIRMED",
        "SHIPPED",
        "CANCELLED",
    ],
)
def test_cancel_order_with_non_pending_status(
    client,
    initial_status,
):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    order = create_order(
        client,
        headers,
        status=initial_status,
    )

    response = client.post(
        f"/orders/{order['id']}/cancel",
        headers=headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Solo se pueden cancelar órdenes PENDING"
    )


# Pruebas faltantes
def test_cancel_order_requires_authentication(client):
    response = client.post("/orders/1/cancel")

    assert response.status_code == 401


def test_cancel_order_not_found(client):
    token = get_token(client)

    response = client.post(
        "/orders/999999/cancel",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 404


# Probar crear y listar órdenes
def test_create_order(client):
    token = get_token(client)

    response = client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "PENDING",
            "items": [
                {
                    "product_name": "Teclado",
                    "quantity": 2,
                    "unit_price": "35.50",
                }
            ],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "PENDING"
    assert len(data["items"]) == 1


def test_list_orders(client):
    token = get_token(client)

    response = client.get(
        "/orders/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


# Aislamiento entre usuarios
def test_users_only_see_their_own_orders(client):
    alice_token = get_token(client)

    create_response = client.post(
        "/orders/",
        headers={
            "Authorization": f"Bearer {alice_token}",
        },
        json={
            "status": "PENDING",
            "items": [
                {
                    "product_name": "Teclado",
                    "quantity": 1,
                    "unit_price": "35.50",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    bob_register_response = client.post(
        "/auth/register",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "secreto123",
        },
    )

    assert bob_register_response.status_code == 201

    bob_login_response = client.post(
        "/auth/login",
        data={
            "username": "bob",
            "password": "secreto123",
        },
    )

    bob_token = bob_login_response.json()["access_token"]

    list_response = client.get(
        "/orders/",
        headers={
            "Authorization": f"Bearer {bob_token}",
        },
    )

    assert list_response.status_code == 200
    assert list_response.json() == []


# Actualizar y eliminar
def test_update_order(client):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/orders/",
        headers=headers,
        json={
            "status": "PENDING",
            "items": [
                {
                    "product_name": "Mouse",
                    "quantity": 1,
                    "unit_price": "20.00",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    response = client.put(
        f"/orders/{order_id}",
        headers=headers,
        json={
            "status": "CONFIRMED",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "CONFIRMED"


def test_delete_order(client):
    token = get_token(client)

    headers = {
        "Authorization": f"Bearer {token}",
    }

    create_response = client.post(
        "/orders/",
        headers=headers,
        json={
            "status": "PENDING",
            "items": [
                {
                    "product_name": "Monitor",
                    "quantity": 1,
                    "unit_price": "150.00",
                }
            ],
        },
    )

    assert create_response.status_code == 201

    order_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert get_response.status_code == 404
