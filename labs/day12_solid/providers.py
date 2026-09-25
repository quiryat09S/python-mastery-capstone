from .ports import OrderRepository
from .service import OrderService


def provide_order_service(
    repository: OrderRepository,
) -> OrderService:
    return OrderService(repository)
