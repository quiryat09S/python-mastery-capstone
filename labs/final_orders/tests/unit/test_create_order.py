from decimal import Decimal

from labs.final_orders.application.dto import (
    CreateOrderInput,
    CreateOrderItemInput,
)
from labs.final_orders.application.use_cases import CreateOrder
from labs.final_orders.infrastructure.event_publisher import (
    InMemoryEventPublisher,
)
from labs.final_orders.infrastructure.memory import InMemoryUnitOfWork


def test_create_order_commits_and_publishes_event():
    unit_of_work = InMemoryUnitOfWork()
    publisher = InMemoryEventPublisher()

    use_case = CreateOrder(
        unit_of_work,
        publisher,
    )

    result = use_case.execute(
        CreateOrderInput(
            user_id=10,
            items=(
                CreateOrderItemInput(
                    product_name="Keyboard",
                    quantity=2,
                    unit_price=Decimal("50.00"),
                ),
            ),
        )
    )

    assert result.id == 1
    assert result.total == Decimal("100.00")
    assert unit_of_work.committed is True
    assert len(publisher.events) == 1
