from typing import Protocol

from ..domain.entities import Order


class OrderRepository(Protocol):
    def next_id(self) -> int: ...

    def save(self, order: Order) -> Order: ...

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None: ...


class OrderNotification(Protocol):
    def order_created(
        self,
        order: Order,
    ) -> None: ...
