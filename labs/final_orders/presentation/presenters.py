from ..domain.entities import Order
from .schemas import OrderResponse


def present_order(
    order: Order,
) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        total=order.total,
        status=order.status.value,
    )
