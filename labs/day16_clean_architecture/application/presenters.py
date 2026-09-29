from decimal import Decimal
from typing import TypedDict

from ..domain.entities import Order


class OrderResponse(TypedDict):
    id: int
    customer_id: int
    total: Decimal
    status: str


def present_order(order: Order) -> OrderResponse:
    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "total": order.total,
        "status": order.status,
    }
