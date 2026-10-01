import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..application.order_commands import CancelOrder, DeleteOrder
from ..application.order_queries import GetOrder, ListOrders
from ..application.use_cases import CreateOrder
from ..infrastructure.database import get_db
from ..infrastructure.event_publisher import InMemoryEventPublisher
from ..infrastructure.models import UserModel
from ..infrastructure.security import ALGORITHM, SECRET_KEY
from ..infrastructure.sqlalchemy_uow import SqlAlchemyUnitOfWork

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login",
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserModel:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={
            "WWW-Authenticate": "Bearer",
        },
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")

        if not isinstance(username, str):
            raise credentials_exception

    except jwt.InvalidTokenError as exc:
        raise credentials_exception from exc

    user = db.query(UserModel).filter(UserModel.username == username).first()

    if user is None:
        raise credentials_exception

    return user


def provide_create_order(
    db: Session,
) -> CreateOrder:
    unit_of_work = SqlAlchemyUnitOfWork(db)
    event_publisher = InMemoryEventPublisher()

    return CreateOrder(
        unit_of_work=unit_of_work,
        event_publisher=event_publisher,
    )


def provide_get_order(
    db: Session,
) -> GetOrder:
    return GetOrder(SqlAlchemyUnitOfWork(db))


def provide_list_orders(
    db: Session,
) -> ListOrders:
    return ListOrders(SqlAlchemyUnitOfWork(db))


def provide_cancel_order(
    db: Session,
) -> CancelOrder:
    return CancelOrder(SqlAlchemyUnitOfWork(db))


def provide_delete_order(
    db: Session,
) -> DeleteOrder:
    return DeleteOrder(SqlAlchemyUnitOfWork(db))
