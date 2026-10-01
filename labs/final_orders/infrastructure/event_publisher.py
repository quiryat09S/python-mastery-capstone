from ..domain.events import OrderCreated


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self.events: list[OrderCreated] = []

    def publish(
        self,
        event: OrderCreated,
    ) -> None:
        self.events.append(event)
