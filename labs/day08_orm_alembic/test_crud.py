from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from labs.day08_orm_alembic.models import Base, Order, OrderItem, User


def crear_test_engine():
    """Crea una base SQLite en memoria para las pruebas."""

    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_create_user_order_and_items():
    engine = crear_test_engine()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username="test_user",
            email="test@example.com",
        )

        order = Order(
            status="PENDING",
        )

        order.items.append(
            OrderItem(
                product_name="Teclado",
                quantity=1,
                unit_price=Decimal("120.50"),
            )
        )

        user.orders.append(order)

        session.add(user)
        session.commit()

        assert user.id is not None
        assert order.id is not None
        assert len(order.items) == 1


def test_read_user_orders():
    engine = crear_test_engine()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username="reader",
            email="reader@example.com",
        )

        order = Order(status="PAID")

        user.orders.append(order)

        session.add(user)
        session.commit()

        stmt = select(Order).join(User).where(User.username == "reader")

        orders = list(session.scalars(stmt).all())

        assert len(orders) == 1
        assert orders[0].status == "PAID"


def test_update_order_status():
    engine = crear_test_engine()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        order = Order(
            status="PENDING",
        )

        user = User(
            username="updater",
            email="updater@example.com",
        )

        user.orders.append(order)

        session.add(user)
        session.commit()

        order.status = "SHIPPED"
        session.commit()

        assert order.status == "SHIPPED"


def test_delete_user_cascades_orders():
    engine = crear_test_engine()

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        user = User(
            username="deleter",
            email="deleter@example.com",
        )

        order = Order(status="PENDING")

        order.items.append(
            OrderItem(
                product_name="Mouse",
                quantity=1,
                unit_price=Decimal("45.00"),
            )
        )

        user.orders.append(order)

        session.add(user)
        session.commit()

        user_id = user.id

        session.delete(user)
        session.commit()

        deleted_user = session.get(User, user_id)

        deleted_order = session.get(
            Order,
            order.id,
        )

        assert deleted_user is None
        assert deleted_order is None
