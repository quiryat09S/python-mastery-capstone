from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from labs.day08_orm_alembic.models import Base

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def init_db() -> None:
    """Crea las tablas en la base de datos en memoria."""
    Base.metadata.create_all(bind=engine)


def get_db_session():  # -> Generator[Session, None, None]:
    """Proporciona una sesión de base de datos."""
    with SessionLocal() as session:
        yield session
