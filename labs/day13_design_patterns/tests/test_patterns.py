from decimal import Decimal
from unittest.mock import Mock

import pytest

from labs.day13_design_patterns.adapters import (
    FakeExternalCatalogClient,
    ProductCatalogAdapter,
)
from labs.day13_design_patterns.decorators import (
    CachedPricingStrategy,
    cached_price,
)
from labs.day13_design_patterns.domain import Product
from labs.day13_design_patterns.services import PricingService
from labs.day13_design_patterns.strategies import (
    PercentageDiscountPricing,
    PremiumPricing,
    RegularPricing,
)


@pytest.fixture()
def product():
    return Product(
        name="Keyboard",
        base_price=Decimal("100.00"),
    )


def test_regular_pricing(product):
    service = PricingService(RegularPricing())

    assert service.calculate_price(product) == Decimal("100.00")


def test_percentage_discount_pricing(product):
    service = PricingService(PercentageDiscountPricing(Decimal("20")))

    assert service.calculate_price(product) == Decimal("80.00")


def test_premium_pricing(product):
    service = PricingService(PremiumPricing())

    assert service.calculate_price(product) == Decimal("90.00")


def test_cached_pricing_strategy_uses_cache(product):
    strategy = Mock()
    strategy.calculate.return_value = Decimal("80.00")

    cached_strategy = CachedPricingStrategy(strategy)

    first_result = cached_strategy.calculate(product)
    second_result = cached_strategy.calculate(product)

    assert first_result == Decimal("80.00")
    assert second_result == Decimal("80.00")
    strategy.calculate.assert_called_once_with(product)


def test_cached_price_decorator(product):
    calculate = Mock(return_value=Decimal("75.00"))
    decorated = cached_price(calculate)

    first_result = decorated(product)
    second_result = decorated(product)

    assert first_result == Decimal("75.00")
    assert second_result == Decimal("75.00")
    calculate.assert_called_once_with(product)


def test_product_catalog_adapter():
    client = FakeExternalCatalogClient(
        products={
            "SKU-001": {
                "display_name": "Keyboard",
                "price": "100.00",
            }
        }
    )

    adapter = ProductCatalogAdapter(client)

    product = adapter.get_product("SKU-001")

    assert product == Product(
        name="Keyboard",
        base_price=Decimal("100.00"),
    )


def test_product_catalog_adapter_raises_for_unknown_product():
    client = FakeExternalCatalogClient(products={})

    adapter = ProductCatalogAdapter(client)

    with pytest.raises(KeyError):
        adapter.get_product("UNKNOWN")
