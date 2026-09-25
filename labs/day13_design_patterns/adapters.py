from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from .domain import Product


class ExternalCatalogClient(Protocol):
    def fetch_product(
        self,
        product_code: str,
    ) -> dict[str, str]: ...


@dataclass
class FakeExternalCatalogClient:
    products: dict[str, dict[str, str]]

    def fetch_product(
        self,
        product_code: str,
    ) -> dict[str, str]:
        return self.products[product_code]


class ProductCatalogAdapter:
    def __init__(
        self,
        client: ExternalCatalogClient,
    ) -> None:
        self._client = client

    def get_product(
        self,
        product_code: str,
    ) -> Product:
        external_product = self._client.fetch_product(product_code)

        return Product(
            name=external_product["display_name"],
            base_price=Decimal(external_product["price"]),
        )
