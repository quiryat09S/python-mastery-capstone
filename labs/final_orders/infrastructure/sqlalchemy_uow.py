from sqlalchemy.orm import Session

from ..application.ports import OrderRepository, UnitOfWork
from .sqlalchemy_repository import SqlAlchemyOrderRepository


class SqlAlchemyUnitOfWork:
    orders: OrderRepository

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session
        self.orders = SqlAlchemyOrderRepository(session)

    def __enter__(self) -> UnitOfWork:
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
