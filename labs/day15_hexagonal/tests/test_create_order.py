from decimal import Decimal
from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from labs.day15_hexagonal.application.dto import (
    CreateOrderInput,
    CreateOrderItemInput,
)
from labs.day15_hexagonal.application.use_cases import CreateOrder
from labs.day15_hexagonal.domain.entities import Order, OrderItem
from labs.day15_hexagonal.infrastructure.memory import (
    InMemoryOrderNotification,
    InMemoryOrderRepository,
)
from labs.day15_hexagonal.infrastructure.notification_http import (
    HttpOrderNotification,
)
from labs.day15_hexagonal.infrastructure.sqlalchemy_adapter import (
    Base,
    SqlAlchemyOrderRepository,
    create_sqlite_engine,
)
from labs.day15_hexagonal.providers import (
    provide_create_order,
    provide_memory_create_order,
)


def build_input() -> CreateOrderInput:
    return CreateOrderInput(
        customer_id=10,
        items=(
            CreateOrderItemInput(
                product_name="Keyboard",
                quantity=2,
                unit_price=Decimal("50.00"),
            ),
        ),
    )


def test_create_order():
    repository = InMemoryOrderRepository()
    notification = InMemoryOrderNotification()
    use_case = CreateOrder(repository, notification)

    result = use_case.execute(build_input())

    assert result.order_id == 1
    assert result.customer_id == 10
    assert result.total == Decimal("100.00")
    assert result.status == "PENDING"
    assert len(notification.created_orders) == 1


def test_create_order_requires_items():
    repository = InMemoryOrderRepository()
    notification = InMemoryOrderNotification()
    use_case = CreateOrder(repository, notification)

    data = CreateOrderInput(
        customer_id=10,
        items=(),
    )

    with pytest.raises(
        ValueError,
        match="al menos un elemento",
    ):
        use_case.execute(data)


# Pruebas de contrato
def test_sqlalchemy_repository_contract():
    engine = create_sqlite_engine()
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        repository = SqlAlchemyOrderRepository(session)
        notification = InMemoryOrderNotification()
        use_case = CreateOrder(repository, notification)

        result = use_case.execute(build_input())

        assert result.order_id == 1
        assert result.customer_id == 10
        assert result.total == Decimal("100.00")
        assert result.status == "PENDING"

    engine.dispose()


def test_http_notification_adapter():
    client = Mock()
    response = Mock()
    client.post.return_value = response

    adapter = HttpOrderNotification(
        endpoint="https://notifications.test/orders",
        client=client,
    )

    order = Order(
        id=1,
        customer_id=10,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=2,
                unit_price=Decimal("50.00"),
            ),
        ),
    )

    adapter.order_created(order)

    client.post.assert_called_once_with(
        "https://notifications.test/orders",
        json={
            "order_id": 1,
            "customer_id": 10,
            "total": "100.00",
            "status": "PENDING",
        },
    )
    response.raise_for_status.assert_called_once()


# Prueba de wiring
def test_memory_provider_wires_create_order():
    use_case = provide_memory_create_order()

    result = use_case.execute(build_input())

    assert result.order_id == 1
    assert result.customer_id == 10
    assert result.total == Decimal("100.00")
    assert result.status == "PENDING"


# Prueba de sustitución de repositorios
def test_use_case_accepts_repository_port():
    repository = InMemoryOrderRepository()
    notification = InMemoryOrderNotification()

    use_case = provide_create_order(
        repository=repository,
        notification=notification,
    )

    result = use_case.execute(build_input())

    assert result.total == Decimal("100.00")
    assert repository.get_by_id(result.order_id) is not None
