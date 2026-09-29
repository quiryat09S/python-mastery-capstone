from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderItem:
    product_name: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: int
    customer_id: int
    items: tuple[OrderItem, ...]
    status: str = "PENDING"

    @property
    def total(self) -> Decimal:
        return sum(
            (item.subtotal for item in self.items),
            Decimal("0.00"),
        )
