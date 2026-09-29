from unittest.mock import Mock, patch

from typer.testing import CliRunner

from labs.day18_cli.cli import app

runner = CliRunner()


def test_help():
    result = runner.invoke(
        app,
        ["--help"],
    )

    assert result.exit_code == 0
    assert "gestionar Orders API" in result.stdout


def test_list_orders():
    fake_response = Mock()
    fake_response.json.return_value = [
        {
            "id": 1,
            "user_id": 1,
            "status": "PENDING",
        }
    ]

    with patch(
        "labs.day18_cli.client.httpx.get",
        return_value=fake_response,
    ):
        result = runner.invoke(
            app,
            ["list"],
        )

    assert result.exit_code == 0
    assert "#1" in result.stdout
    assert "PENDING" in result.stdout


def test_list_orders_empty():
    fake_response = Mock()
    fake_response.json.return_value = []

    with patch(
        "labs.day18_cli.client.httpx.get",
        return_value=fake_response,
    ):
        result = runner.invoke(
            app,
            ["list"],
        )

    assert result.exit_code == 0
    assert "No hay órdenes." in result.stdout


def test_create_order():
    fake_response = Mock()
    fake_response.json.return_value = {
        "id": 10,
        "user_id": 1,
        "status": "PENDING",
    }

    with patch(
        "labs.day18_cli.client.httpx.post",
        return_value=fake_response,
    ):
        result = runner.invoke(
            app,
            [
                "create",
                "--product-name",
                "Keyboard",
                "--quantity",
                "2",
                "--unit-price",
                "50.00",
            ],
        )

    assert result.exit_code == 0
    assert "Orden creada: #10" in result.stdout


def test_delete_order():
    fake_response = Mock()

    with patch(
        "labs.day18_cli.client.httpx.delete",
        return_value=fake_response,
    ):
        result = runner.invoke(
            app,
            [
                "delete",
                "10",
            ],
        )

    assert result.exit_code == 0
    assert "Orden eliminada: #10" in result.stdout
