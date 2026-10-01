def test_complete_orders_flow(client):
    register_response = client.post(
        "/auth/register",
        json={
            "username": "e2e_user",
            "email": "e2e@example.com",
            "password": "secreto123",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        data={
            "username": "e2e_user",
            "password": "secreto123",
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}",
    }

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

    order_id = create_response.json()["id"]

    get_response = client.get(
        f"/orders/{order_id}",
        headers=headers,
    )

    assert get_response.status_code == 200

    cancel_response = client.post(
        f"/orders/{order_id}/cancel",
        headers=headers,
    )

    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "CANCELLED"
