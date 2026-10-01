from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

DATABASE_URL = "sqlite:///./final_orders.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={
        "check_same_thread": False,
    },
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
