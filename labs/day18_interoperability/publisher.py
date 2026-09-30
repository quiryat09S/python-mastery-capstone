import json
from dataclasses import asdict, dataclass

import redis


@dataclass(frozen=True)
class OrderCreated:
    order_id: int
    customer_id: int
    status: str
    total: float


class RedisOrderPublisher:
    def __init__(
        self,
        client: redis.Redis,
        channel: str = "orders.created",
    ) -> None:
        self._client = client
        self._channel = channel

    def publish(
        self,
        event: OrderCreated,
    ) -> None:
        payload = json.dumps(asdict(event))

        self._client.publish(
            self._channel,
            payload,
        )
