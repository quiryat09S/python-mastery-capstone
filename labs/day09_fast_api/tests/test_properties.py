from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from labs.day09_fast_api.schemas import OrderItemCreate


@given(
    product_name=st.text(
        min_size=1,
        max_size=100,
    ),
    quantity=st.integers(
        min_value=1,
        max_value=1000,
    ),
    unit_price=st.decimals(
        min_value="0.01",
        max_value="100000.00",
        places=2,
        allow_nan=False,
        allow_infinity=False,
    ),
)
def test_order_item_accepts_valid_properties(
    product_name: str,
    quantity: int,
    unit_price: Decimal,
) -> None:
    item = OrderItemCreate(
        product_name=product_name,
        quantity=quantity,
        unit_price=unit_price,
    )

    assert 1 <= len(item.product_name) <= 100
    assert item.quantity > 0
    assert item.unit_price > Decimal("0")
