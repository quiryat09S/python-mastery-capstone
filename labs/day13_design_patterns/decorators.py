from collections.abc import Callable
from functools import wraps

from .domain import Product
from .strategies import PricingStrategy


def cached_price[
    T
](function: Callable[[Product], T],) -> Callable[[Product], T]:
    cache: dict[Product, T] = {}

    @wraps(function)
    def wrapper(product: Product) -> T:
        if product not in cache:
            cache[product] = function(product)

        return cache[product]

    return wrapper


class CachedPricingStrategy:
    def __init__(
        self,
        strategy: PricingStrategy,
    ) -> None:
        self._strategy = strategy
        self._cache: dict[Product, object] = {}

    def calculate(
        self,
        product: Product,
    ) -> object:
        if product not in self._cache:
            self._cache[product] = self._strategy.calculate(product)

        return self._cache[product]
