from sqlalchemy import select
from sqlalchemy.orm import Session

from .domain import Order
from .sql_models import OrderModel


class SqlAlchemyOrderRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def save(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            customer=order.customer,
            total=order.total,
        )

        self._session.merge(model)
        self._session.commit()

        return order

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        model = self._session.scalar(
            select(OrderModel).where(OrderModel.id == order_id)
        )

        if model is None:
            return None

        return Order(
            id=model.id,
            customer=model.customer,
            total=model.total,
        )
