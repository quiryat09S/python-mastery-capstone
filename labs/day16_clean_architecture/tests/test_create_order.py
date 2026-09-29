from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from labs.day16_clean_architecture.application.use_cases import (
    CreateOrder,
    CreateOrderInput,
)
from labs.day16_clean_architecture.domain.entities import OrderItem
from labs.day16_clean_architecture.infrastructure.sqlalchemy_uow import (
    Base,
    SqlAlchemyUnitOfWork,
    create_sqlite_engine,
)
from labs.day16_clean_architecture.infrastructure.unit_of_work import (
    InMemoryEventPublisher,
    InMemoryUnitOfWork,
)


def build_input() -> CreateOrderInput:
    return CreateOrderInput(
        customer_id=10,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=2,
                unit_price=Decimal("50.00"),
            ),
        ),
    )


def test_create_order_commits_and_publishes_event():
    unit_of_work = InMemoryUnitOfWork()
    event_publisher = InMemoryEventPublisher()

    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    result = use_case.execute(build_input())

    assert result == {
        "id": 1,
        "customer_id": 10,
        "total": Decimal("100.00"),
        "status": "PENDING",
    }

    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False
    assert len(event_publisher.events) == 1

    event = event_publisher.events[0]

    assert event.order_id == 1
    assert event.customer_id == 10
    assert event.total == Decimal("100.00")


def test_presenter_returns_expected_structure():
    unit_of_work = InMemoryUnitOfWork()
    event_publisher = InMemoryEventPublisher()
    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    result = use_case.execute(build_input())

    assert set(result) == {
        "id",
        "customer_id",
        "total",
        "status",
    }


def test_create_order_requires_items():
    unit_of_work = InMemoryUnitOfWork()
    event_publisher = InMemoryEventPublisher()
    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    with pytest.raises(
        ValueError,
        match="al menos un elemento",
    ):
        use_case.execute(
            CreateOrderInput(
                customer_id=10,
                items=(),
            )
        )

    assert unit_of_work.committed is False


class FailingUnitOfWork(InMemoryUnitOfWork):
    def commit(self) -> None:
        raise RuntimeError("Error de persistencia")


def test_create_order_rolls_back_when_commit_fails():
    unit_of_work = FailingUnitOfWork()
    event_publisher = InMemoryEventPublisher()
    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    with pytest.raises(
        RuntimeError,
        match="Error de persistencia",
    ):
        use_case.execute(build_input())

    assert unit_of_work.committed is False
    assert unit_of_work.rolled_back is True
    assert event_publisher.events == []


def test_sqlalchemy_unit_of_work():
    engine = create_sqlite_engine()
    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        unit_of_work = SqlAlchemyUnitOfWork(session)
        event_publisher = InMemoryEventPublisher()
        use_case = CreateOrder(
            unit_of_work,
            event_publisher,
        )

        result = use_case.execute(build_input())

        assert result["id"] == 1
        assert result["total"] == Decimal("100.00")
        assert len(event_publisher.events) == 1

    engine.dispose()


# Prueba de orden de operaciones
class TrackingUnitOfWork(InMemoryUnitOfWork):
    def __init__(
        self,
        operations: list[str],
    ) -> None:
        super().__init__()
        self.operations = operations

    def commit(self) -> None:
        self.operations.append("commit")
        super().commit()


class TrackingPublisher(InMemoryEventPublisher):
    def __init__(self, operations: list[str]):
        super().__init__()
        self.operations = operations

    def publish(self, event):
        self.operations.append("publish")
        super().publish(event)


def test_event_is_published_after_commit():
    operations: list[str] = []

    unit_of_work = TrackingUnitOfWork(operations)
    event_publisher = TrackingPublisher(operations)

    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    use_case.execute(build_input())

    assert operations == [
        "commit",
        "publish",
    ]
