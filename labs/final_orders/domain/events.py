from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderCreated:
    order_id: int
    user_id: int
    total: Decimal
