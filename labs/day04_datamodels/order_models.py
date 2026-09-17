from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# --- 1. DTO de Entrada (Pydantic v2) ---
class ItemIn(BaseModel):
    name: str = Field(..., min_length=1)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=1, gt=0)


class OrderIn(BaseModel):
    customer_email: EmailStr
    items: list[ItemIn]

    @field_validator("items")
    @classmethod
    def validar_items_no_vacios(cls, items: list[ItemIn]) -> list[ItemIn]:
        if not items:
            raise ValueError("La orden debe incluir al menos un producto")
        return items


# --- 2. Entidad de Dominio (Dataclass con Comportamiento) ---
@dataclass
class OrderItem:
    name: str
    price: float
    quantity: int = 1

    @property
    def subtotal(self) -> float:
        return round(self.price * self.quantity, 2)


@dataclass
class Order:
    id: str
    customer_email: str
    items: list[OrderItem]
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_amount(self) -> float:
        return round(sum(item.subtotal for item in self.items), 2)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Order):
            return NotImplemented
        return self.id == other.id

    def __lt__(self, other: Order) -> bool:
        """Permite ordenar/comparar órdenes por su monto total."""
        return self.total_amount < other.total_amount


# --- 3. DTO de Salida (Pydantic v2) ---
class OrderOut(BaseModel):
    id: str
    customer_email: EmailStr
    total_amount: float
    items_count: int
    created_at: datetime


# --- 4. Mapeadores / Conversiones ---
def crear_orden_desde_dto(order_id: str, dto: OrderIn) -> Order:
    items_dominio = [
        OrderItem(name=item.name, price=item.price, quantity=item.quantity)
        for item in dto.items
    ]
    return Order(
        id=order_id, customer_email=str(dto.customer_email), items=items_dominio
    )


def exportar_orden_dto(order: Order) -> OrderOut:
    return OrderOut(
        id=order.id,
        customer_email=order.customer_email,
        total_amount=order.total_amount,
        items_count=len(order.items),
        created_at=order.created_at,
    )


if __name__ == "__main__":
    payload_raw = {
        "customer_email": "cliente@empresa.com",
        "items": [
            {"name": "Monitor 274k", "price": 350.50, "quantity": 1},
            {"name": "Cable HDMI", "price": 12.00, "quantity": 2},
        ],
    }

    # Validar entrada
    dto_in = OrderIn(**payload_raw)
    print(" Entrada validada correctamente con Pydantic")

    # Transformar a Entidad de Dominio
    orden_1 = crear_orden_desde_dto("ORD-001", dto_in)
    print(
        f" Entidad Dominio Creada -> ID: {orden_1.id} | Total: ${orden_1.total_amount}"
    )

    # Probar comparación (dunder __lt__)
    orden_2 = Order(
        id="ORD-002",
        customer_email="cliente2@empresa.com",
        items=[OrderItem(name="Mousepad", price=15.00, quantity=1)],
    )
    print(
        f" ¿Orden 2 (${orden_2.total_amount}) < Orden 1 (${orden_1.total_amount})?: {orden_2 < orden_1}"
    )

    # Exportar a DTO de salida
    dto_out = exportar_orden_dto(orden_1)
    print(" JSON de Salida listo para API:", dto_out.model_dump_json(indent=2))
