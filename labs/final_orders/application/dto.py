from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class CreateOrderItemInput:
    product_name: str
    quantity: int
    unit_price: Decimal


@dataclass(frozen=True)
class CreateOrderInput:
    user_id: int
    items: tuple[CreateOrderItemInput, ...]
