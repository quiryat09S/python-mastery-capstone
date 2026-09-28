from ..application.ports import OrderNotification, OrderRepository
from ..domain.entities import Order


class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._orders: dict[int, Order] = {}
        self._sequence = 0

    def next_id(self) -> int:
        self._sequence += 1
        return self._sequence

    def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        return self._orders.get(order_id)


class InMemoryOrderNotification(OrderNotification):
    def __init__(self) -> None:
        self.created_orders: list[Order] = []

    def order_created(self, order: Order) -> None:
        self.created_orders.append(order)
