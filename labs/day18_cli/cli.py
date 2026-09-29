import typer

from .client import OrdersClient
from .config import load_settings

app = typer.Typer(
    help="CLI para gestionar Orders API.",
)


def get_client(token: str | None) -> OrdersClient:
    settings = load_settings()

    return OrdersClient(
        base_url=settings.api_url,
        timeout=settings.timeout,
        token=token,
    )


@app.command("list")
def list_orders(
    token: str | None = typer.Option(
        default=None,
        envvar="ORDERS_API_TOKEN",
        help="Token JWT.",
    ),
) -> None:
    client = get_client(token)
    orders = client.list_orders()

    if not orders:
        typer.echo("No hay órdenes.")

        return

    for order in orders:
        typer.echo(
            f"#{order['id']} "
            f"customer={order['user_id']} "
            f"status={order['status']}"
        )


@app.command()
def create(
    status: str = typer.Option(
        default="PENDING",
        help="Estado de la orden.",
    ),
    product_name: str = typer.Option(
        ...,
        prompt="Nombre del producto",
    ),
    quantity: int = typer.Option(
        ...,
        min=1,
        prompt="Cantidad",
    ),
    unit_price: float = typer.Option(
        ...,
        min=0.01,
        prompt="Precio unitario",
    ),
    token: str | None = typer.Option(
        default=None,
        envvar="ORDERS_API_TOKEN",
        help="Token JWT.",
    ),
) -> None:
    client = get_client(token)

    order = client.create_order(
        status=status,
        items=[
            {
                "product_name": product_name,
                "quantity": quantity,
                "unit_price": unit_price,
            }
        ],
    )

    typer.echo(f"Orden creada: #{order['id']}")


@app.command()
def delete(
    order_id: int = typer.Argument(
        ...,
        min=1,
    ),
    token: str | None = typer.Option(
        default=None,
        envvar="ORDERS_API_TOKEN",
        help="Token JWT.",
    ),
) -> None:
    client = get_client(token)
    client.delete_order(order_id)

    typer.echo(f"Orden eliminada: #{order_id}")


if __name__ == "__main__":
    app()
