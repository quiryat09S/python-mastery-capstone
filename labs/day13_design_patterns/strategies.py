from decimal import Decimal
from typing import Protocol

from .domain import Product


class PricingStrategy(Protocol):
    def calculate(
        self,
        product: Product,
    ) -> Decimal: ...


class RegularPricing:
    def calculate(
        self,
        product: Product,
    ) -> Decimal:
        return product.base_price


class PercentageDiscountPricing:
    def __init__(
        self,
        percentage: Decimal,
    ) -> None:
        self.percentage = percentage

    def calculate(
        self,
        product: Product,
    ) -> Decimal:
        discount = product.base_price * self.percentage / Decimal("100")

        return product.base_price - discount


class PremiumPricing:
    def calculate(
        self,
        product: Product,
    ) -> Decimal:
        return product.base_price * Decimal("0.90")
