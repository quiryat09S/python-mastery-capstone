from typing import Protocol

from .domain import Order


class OrderRepository(Protocol):
    def save(self, order: Order) -> Order: ...

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None: ...
