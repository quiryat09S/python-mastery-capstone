from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum

from .exceptions import InvalidOrderError, InvalidOrderStateError


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class OrderItem:
    product_name: str
    quantity: int
    unit_price: Decimal

    def __post_init__(self) -> None:
        if not self.product_name.strip():
            raise InvalidOrderError("El nombre del producto es obligatorio")

        if self.quantity <= 0:
            raise InvalidOrderError("La cantidad debe ser mayor que cero")

        if self.unit_price <= 0:
            raise InvalidOrderError("El precio debe ser mayor que cero")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: int
    user_id: int
    items: tuple[OrderItem, ...]
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self) -> None:
        if not self.items:
            raise InvalidOrderError(
                "La orden debe contener al menos un elemento"
            )

    @property
    def total(self) -> Decimal:
        return sum(
            (item.subtotal for item in self.items),
            Decimal("0.00"),
        )

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateError(
                "Solo se pueden confirmar órdenes PENDING"
            )

        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateError(
                "Solo se pueden cancelar órdenes PENDING"
            )

        self.status = OrderStatus.CANCELLED
