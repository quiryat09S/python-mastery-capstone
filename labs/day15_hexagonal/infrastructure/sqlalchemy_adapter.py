from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from ..application.ports import OrderRepository
from ..domain.entities import Order


class Base(DeclarativeBase):
    pass


class OrderRow(Base):
    __tablename__ = "hexagonal_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    customer_id: Mapped[int] = mapped_column(
        nullable=False,
    )

    total: Mapped[Decimal] = mapped_column(
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        nullable=False,
    )


class SqlAlchemyOrderRepository(OrderRepository):
    def __init__(
        self,
        session: Session,
    ) -> None:
        self._session = session

    def next_id(self) -> int:
        last_id = self._session.scalar(
            select(OrderRow.id).order_by(OrderRow.id.desc())
        )

        return (last_id or 0) + 1

    def save(
        self,
        order: Order,
    ) -> Order:
        row = OrderRow(
            id=order.id,
            customer_id=order.customer_id,
            total=order.total,
            status=order.status,
        )

        self._session.merge(row)
        self._session.commit()

        return order

    def get_by_id(
        self,
        order_id: int,
    ) -> Order | None:
        row = self._session.get(
            OrderRow,
            order_id,
        )

        if row is None:
            return None

        return Order(
            id=row.id,
            customer_id=row.customer_id,
            items=(),
            status=row.status,
        )


def create_sqlite_engine():
    return create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
    )
