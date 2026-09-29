from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class OrdersClient:
    base_url: str
    timeout: float = 10.0
    token: str | None = None

    def _headers(self) -> dict[str, str]:
        if self.token is None:
            return {}

        return {
            "Authorization": f"Bearer {self.token}",
        }

    def list_orders(self) -> list[dict[str, Any]]:
        response = httpx.get(
            f"{self.base_url}/orders/",
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def create_order(
        self,
        status: str,
        items: list[dict[str, Any]],
    ) -> dict[str, Any]:
        response = httpx.post(
            f"{self.base_url}/orders/",
            headers=self._headers(),
            json={
                "status": status,
                "items": items,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def delete_order(
        self,
        order_id: int,
    ) -> None:
        response = httpx.delete(
            f"{self.base_url}/orders/{order_id}",
            headers=self._headers(),
            timeout=self.timeout,
        )
        response.raise_for_status()
