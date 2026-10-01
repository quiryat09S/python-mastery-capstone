from ..domain.entities import Order
from .ports import UnitOfWork


class GetOrder:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self,
        order_id: int,
        user_id: int,
    ) -> Order | None:
        with self._unit_of_work as uow:
            order = uow.orders.get_by_id(order_id)

        if order is None:
            return None

        if order.user_id != user_id:
            return None

        return order


class ListOrders:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self,
        user_id: int,
    ) -> list[Order]:
        with self._unit_of_work as uow:
            return uow.orders.list_by_user(user_id)
