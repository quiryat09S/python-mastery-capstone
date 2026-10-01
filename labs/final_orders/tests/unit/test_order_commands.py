from decimal import Decimal

import pytest

from labs.final_orders.application.order_commands import (
    CancelOrder,
    DeleteOrder,
)
from labs.final_orders.domain.entities import Order, OrderItem, OrderStatus
from labs.final_orders.domain.exceptions import (
    InvalidOrderStateError,
    OrderNotFoundError,
)
from labs.final_orders.infrastructure.memory import InMemoryUnitOfWork


def build_order(
    order_id: int,
    user_id: int,
) -> Order:
    return Order(
        id=order_id,
        user_id=user_id,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=1,
                unit_price=Decimal("50.00"),
            ),
        ),
    )


def test_cancel_order_changes_status_and_commits():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = CancelOrder(unit_of_work)

    result = use_case.execute(
        order_id=1,
        user_id=10,
    )

    assert result.status == OrderStatus.CANCELLED
    assert unit_of_work.committed is True


def test_cancel_order_rejects_non_owner():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = CancelOrder(unit_of_work)

    with pytest.raises(OrderNotFoundError):
        use_case.execute(
            order_id=1,
            user_id=99,
        )


def test_cancel_order_rejects_invalid_state():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)
    order.confirm()

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = CancelOrder(unit_of_work)

    with pytest.raises(InvalidOrderStateError):
        use_case.execute(
            order_id=1,
            user_id=10,
        )


def test_delete_order_removes_order():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = DeleteOrder(unit_of_work)

    use_case.execute(
        order_id=1,
        user_id=10,
    )

    with unit_of_work as uow:
        assert uow.orders.get_by_id(1) is None


def test_delete_order_raises_for_missing_order():
    unit_of_work = InMemoryUnitOfWork()
    use_case = DeleteOrder(unit_of_work)

    with pytest.raises(OrderNotFoundError):
        use_case.execute(
            order_id=999,
            user_id=10,
        )
