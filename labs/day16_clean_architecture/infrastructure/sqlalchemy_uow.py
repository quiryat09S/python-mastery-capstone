from decimal import Decimal

from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from ..domain.entities import Order


class Base(DeclarativeBase):
    pass


class OrderRow(Base):
    __tablename__ = "clean_orders"

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


class SqlAlchemyOrderRepository:
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

    def save(self, order: Order) -> None:
        self._session.merge(
            OrderRow(
                id=order.id,
                customer_id=order.customer_id,
                total=order.total,
                status=order.status,
            )
        )

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


class SqlAlchemyUnitOfWork:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session
        self.orders = SqlAlchemyOrderRepository(session)

    def __enter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

        self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()


def create_sqlite_engine():
    return create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
    )
