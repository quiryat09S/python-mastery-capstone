from .domain import Order
from .ports import OrderRepository


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
    ) -> None:
        self._repository = repository

    def create_order(
        self,
        order: Order,
    ) -> Order:
        return self._repository.save(order)

    def find_order(
        self,
        order_id: int,
    ) -> Order | None:
        return self._repository.get_by_id(order_id)
