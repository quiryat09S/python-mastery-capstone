from decimal import Decimal

from .application.use_cases import CreateOrder, CreateOrderInput
from .domain.entities import OrderItem
from .infrastructure.unit_of_work import (
    InMemoryEventPublisher,
    InMemoryUnitOfWork,
)


def main() -> None:
    unit_of_work = InMemoryUnitOfWork()
    event_publisher = InMemoryEventPublisher()

    use_case = CreateOrder(
        unit_of_work,
        event_publisher,
    )

    input_data = CreateOrderInput(
        customer_id=42,
        items=(
            OrderItem(
                product_name="Keyboard",
                quantity=2,
                unit_price=Decimal("50.00"),
            ),
            OrderItem(
                product_name="Mouse",
                quantity=1,
                unit_price=Decimal("25.00"),
            ),
        ),
    )

    result = use_case.execute(input_data)

    print("=== Arquitectura Limpia: CreateOrder ===")
    print(f"Orden creada: {result['id']}")
    print(f"Cliente: {result['customer_id']}")
    print(f"Total: ${result['total']}")
    print(f"Estado: {result['status']}")
    print(f"Transacción confirmada: {unit_of_work.committed}")
    print(f"Rollback ejecutado: " f"{unit_of_work.rolled_back}")
    print(f"Eventos publicados: " f"{len(event_publisher.events)}")

    if event_publisher.events:
        event = event_publisher.events[0]

        print("Evento: OrderCreated")
        print(f"  order_id: {event.order_id}")
        print(f"  customer_id: {event.customer_id}")
        print(f"  total: ${event.total}")


if __name__ == "__main__":
    main()
