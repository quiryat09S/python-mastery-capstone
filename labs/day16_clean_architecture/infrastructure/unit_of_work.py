from ..application.ports import OrderRepository, UnitOfWork
from ..domain.events import OrderCreated
from .repositories import InMemoryOrderRepository


class InMemoryUnitOfWork:
    orders: OrderRepository

    def __init__(self) -> None:
        self.orders = InMemoryOrderRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> UnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.events: list[OrderCreated] = []

    def publish(self, event: OrderCreated) -> None:
        self.events.append(event)
