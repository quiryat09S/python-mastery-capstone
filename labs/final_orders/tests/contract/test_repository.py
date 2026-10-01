from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from labs.final_orders.domain.entities import Order, OrderItem
from labs.final_orders.infrastructure.models import Base
from labs.final_orders.infrastructure.sqlalchemy_repository import (
    SqlAlchemyOrderRepository,
)


def test_sqlalchemy_repository_round_trip():
    engine = create_engine("sqlite://")

    Base.metadata.create_all(bind=engine)

    with Session(engine) as session:
        repository = SqlAlchemyOrderRepository(session)

        order = Order(
            id=1,
            user_id=10,
            items=(
                OrderItem(
                    product_name="Keyboard",
                    quantity=2,
                    unit_price=Decimal("50.00"),
                ),
            ),
        )

        repository.save(order)
        session.commit()

        result = repository.get_by_id(1)

        assert result is not None
        assert result.id == 1
        assert result.user_id == 10
        assert result.total == Decimal("100.00")
        assert len(result.items) == 1

    engine.dispose()
