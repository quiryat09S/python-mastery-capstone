from decimal import Decimal

import pytest

from labs.final_orders.domain.entities import Order, OrderItem, OrderStatus
from labs.final_orders.domain.exceptions import InvalidOrderError


def test_order_calculates_total():
    order = Order(
        id=1,
        user_id=10,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=2,
                unit_price=Decimal("50.00"),
            ),
            OrderItem(
                product_name="Mouse",
                quantity=1,
                unit_price=Decimal("25.00"),
            ),
        ),
    )

    assert order.total == Decimal("125.00")
    assert order.status == OrderStatus.PENDING


def test_order_cannot_be_empty():
    with pytest.raises(
        InvalidOrderError,
        match="al menos un elemento",
    ):
        Order(
            id=1,
            user_id=10,
            items=(),
        )


def test_order_item_rejects_invalid_quantity():
    with pytest.raises(
        InvalidOrderError,
        match="mayor que cero",
    ):
        OrderItem(
            product_name="Keyboard",
            quantity=0,
            unit_price=Decimal("50.00"),
        )


def test_order_can_be_cancelled_when_pending():
    order = Order(
        id=1,
        user_id=10,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=1,
                unit_price=Decimal("50.00"),
            ),
        ),
    )

    order.cancel()

    assert order.status == OrderStatus.CANCELLED
