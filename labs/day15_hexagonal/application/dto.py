from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateOrderItemInput:
    product_name: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderInput:
    customer_id: int
    items: tuple[CreateOrderItemInput, ...]


@dataclass(frozen=True)
class OrderOutput:
    order_id: int
    customer_id: int
    total: Decimal
    status: str
