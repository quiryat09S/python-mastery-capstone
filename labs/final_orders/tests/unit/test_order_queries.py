from decimal import Decimal

from labs.final_orders.application.order_queries import GetOrder, ListOrders
from labs.final_orders.domain.entities import Order, OrderItem
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


def test_get_order_returns_order_for_owner():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = GetOrder(unit_of_work)

    result = use_case.execute(
        order_id=1,
        user_id=10,
    )

    assert result == order


def test_get_order_hides_other_users_orders():
    unit_of_work = InMemoryUnitOfWork()
    order = build_order(1, 10)

    with unit_of_work as uow:
        uow.orders.save(order)

    use_case = GetOrder(unit_of_work)

    result = use_case.execute(
        order_id=1,
        user_id=99,
    )

    assert result is None


def test_list_orders_returns_only_user_orders():
    unit_of_work = InMemoryUnitOfWork()

    with unit_of_work as uow:
        uow.orders.save(build_order(1, 10))
        uow.orders.save(build_order(2, 20))

    use_case = ListOrders(unit_of_work)

    result = use_case.execute(user_id=10)

    assert [order.id for order in result] == [1]
