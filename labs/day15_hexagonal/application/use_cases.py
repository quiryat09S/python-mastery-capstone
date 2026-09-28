from ..domain.entities import Order, OrderItem
from .dto import CreateOrderInput, OrderOutput
from .ports import OrderNotification, OrderRepository


class CreateOrder:
    def __init__(
        self,
        repository: OrderRepository,
        notification: OrderNotification,
    ) -> None:
        self._repository = repository
        self._notification = notification

    def execute(
        self,
        data: CreateOrderInput,
    ) -> OrderOutput:
        if not data.items:
            raise ValueError("La orden debe contener al menos un elemento")

        items = tuple(
            OrderItem(
                product_name=item.product_name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in data.items
        )

        order = Order(
            id=self._repository.next_id(),
            customer_id=data.customer_id,
            items=items,
        )

        saved_order = self._repository.save(order)
        self._notification.order_created(saved_order)

        return OrderOutput(
            order_id=saved_order.id,
            customer_id=saved_order.customer_id,
            total=saved_order.total,
            status=saved_order.status,
        )
