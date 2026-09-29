from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderCreated:
    order_id: int
    customer_id: int
    total: Decimal
