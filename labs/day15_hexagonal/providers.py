from .application.ports import OrderNotification, OrderRepository
from .application.use_cases import CreateOrder
from .infrastructure.memory import (
    InMemoryOrderNotification,
    InMemoryOrderRepository,
)


def provide_memory_create_order() -> CreateOrder:
    repository: OrderRepository = InMemoryOrderRepository()
    notification: OrderNotification = InMemoryOrderNotification()

    return CreateOrder(
        repository=repository,
        notification=notification,
    )


def provide_create_order(
    repository: OrderRepository,
    notification: OrderNotification,
) -> CreateOrder:
    return CreateOrder(
        repository=repository,
        notification=notification,
    )
