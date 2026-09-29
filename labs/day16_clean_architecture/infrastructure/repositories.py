from ..domain.entities import Order


class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._sequence = 0

    def next_id(self) -> int:
        self._sequence += 1
        return self._sequence

    def save(self, order: Order) -> None:
        self._orders[order.id] = order

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        return self._orders.get(order_id)
