from dataclasses import dataclass

from ..domain.entities import Order, OrderItem
from ..domain.events import OrderCreated
from .ports import EventPublisher, UnitOfWork
from .presenters import OrderResponse, present_order


@dataclass(frozen=True)
class CreateOrderInput:
    customer_id: int
    items: tuple[OrderItem, ...]


class CreateOrder:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        event_publisher: EventPublisher,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._event_publisher = event_publisher

    def execute(
        self,
        data: CreateOrderInput,
    ) -> OrderResponse:
        if not data.items:
            raise ValueError("La orden debe contener al menos un elemento")

        with self._unit_of_work as uow:
            order = Order(
                id=uow.orders.next_id(),
                customer_id=data.customer_id,
                items=data.items,
            )

            uow.orders.save(order)
            uow.commit()

        self._event_publisher.publish(
            OrderCreated(
                order_id=order.id,
                customer_id=order.customer_id,
                total=order.total,
            )
        )

        return present_order(order)
