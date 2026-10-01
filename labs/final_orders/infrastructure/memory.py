from ..application.ports import OrderRepository
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

    def list_by_user(
        self,
        user_id: int,
    ) -> list[Order]:
        return [
            order
            for order in self._orders.values()
            if order.user_id == user_id
        ]

    def delete(self, order: Order) -> None:
        self._orders.pop(order.id, None)


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self.orders: OrderRepository = InMemoryOrderRepository()
        self.committed = False
        self.rolled_back = False

    def __enter__(self) -> "InMemoryUnitOfWork":
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
