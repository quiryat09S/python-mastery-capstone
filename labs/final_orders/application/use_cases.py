from ..domain.entities import Order, OrderItem
from ..domain.events import OrderCreated
from .dto import CreateOrderInput
from .ports import EventPublisher, UnitOfWork


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
    ) -> Order:
        items = tuple(
            OrderItem(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in data.items
        )

        with self._unit_of_work as uow:
            order = Order(
                id=uow.orders.next_id(),
                user_id=data.user_id,
                items=items,
            )

            uow.orders.save(order)
            uow.commit()

        self._event_publisher.publish(
            OrderCreated(
                order_id=order.id,
                user_id=order.user_id,
                total=order.total,
            )
        )

        return order
