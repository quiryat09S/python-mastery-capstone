from typing import Protocol

from ..domain.entities import Order
from ..domain.events import OrderCreated


class OrderRepository(Protocol):
    def next_id(self) -> int: ...

    def save(self, order: Order) -> None: ...

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None: ...

    def list_by_user(
        self,
        user_id: int,
    ) -> list[Order]: ...

    def delete(self, order: Order) -> None: ...


class UnitOfWork(Protocol):
    orders: OrderRepository

    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class EventPublisher(Protocol):
    def publish(self, event: OrderCreated) -> None: ...
