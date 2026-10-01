from ..domain.entities import Order
from ..domain.exceptions import OrderNotFoundError
from .ports import UnitOfWork


class CancelOrder:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self,
        order_id: int,
        user_id: int,
    ) -> Order:
        with self._unit_of_work as uow:
            order = uow.orders.get_by_id(order_id)

            if order is None:
                raise OrderNotFoundError("Order no encontrada")

            if order.user_id != user_id:
                raise OrderNotFoundError("Order no encontrada")

            order.cancel()
            uow.orders.save(order)
            uow.commit()

            return order


class DeleteOrder:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
    ) -> None:
        self._unit_of_work = unit_of_work

    def execute(
        self,
        order_id: int,
        user_id: int,
    ) -> None:
        with self._unit_of_work as uow:
            order = uow.orders.get_by_id(order_id)

            if order is None:
                raise OrderNotFoundError("Order no encontrada")

            if order.user_id != user_id:
                raise OrderNotFoundError("Order no encontrada")

            uow.orders.delete(order)
            uow.commit()
