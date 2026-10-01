from decimal import Decimal

from labs.final_orders.domain.entities import Order, OrderItem
from labs.final_orders.infrastructure.memory import InMemoryOrderRepository


def test_repository_contract():
    repository = InMemoryOrderRepository()

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

    repository.save(order)

    assert repository.get_by_id(1) == order
    assert repository.list_by_user(10) == [order]

    repository.delete(order)

    assert repository.get_by_id(1) is None
