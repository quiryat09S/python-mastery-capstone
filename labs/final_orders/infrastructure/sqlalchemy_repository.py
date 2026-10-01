from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..domain.entities import Order, OrderItem, OrderStatus
from .models import OrderItemModel, OrderModel


class SqlAlchemyOrderRepository:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def next_id(self) -> int:
        last_id = self._session.scalar(select(func.max(OrderModel.id)))

        return (last_id or 0) + 1

    def save(self, order: Order) -> None:
        order_model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            status=order.status.value,
            total=order.total,
        )

        self._session.merge(order_model)

        for item in order.items:
            self._session.add(
                OrderItemModel(
                    order_id=order.id,
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
            )

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        order_model = self._session.get(
            OrderModel,
            order_id,
        )

        if order_model is None:
            return None

        item_models = self._session.scalars(
            select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        ).all()

        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            status=OrderStatus(order_model.status),
            items=tuple(
                OrderItem(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in item_models
            ),
        )

    def list_by_user(
        self,
        user_id: int,
    ) -> list[Order]:
        order_models = self._session.scalars(
            select(OrderModel).where(OrderModel.user_id == user_id)
        ).all()

        orders = []

        for order_model in order_models:
            order = self.get_by_id(order_model.id)

            if order is not None:
                orders.append(order)

        return orders

    def delete(self, order: Order) -> None:
        order_model = self._session.get(
            OrderModel,
            order.id,
        )

        if order_model is not None:
            self._session.delete(order_model)
