from .domain import Product
from .strategies import PricingStrategy


class PricingService:
    def __init__(
        self,
        strategy: PricingStrategy,
    ) -> None:
        self.strategy = strategy

    def calculate_price(
        self,
        product: Product,
    ):
        return self.strategy.calculate(product)
