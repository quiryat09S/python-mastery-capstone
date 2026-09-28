from dataclasses import dataclass

import httpx

from ..domain.entities import Order


@dataclass
class HttpOrderNotification:
    endpoint: str
    client: httpx.Client

    def order_created(self, order: Order) -> None:
        response = self.client.post(
            self.endpoint,
            json={
                "order_id": order.id,
                "customer_id": order.customer_id,
                "total": str(order.total),
                "status": order.status,
            },
        )

        response.raise_for_status()
