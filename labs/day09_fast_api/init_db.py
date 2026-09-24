from sqlalchemy import select

from .auth import hash_password
from .database import SessionLocal, engine
from .models import Base, User


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.id == 1))

        if user is None:
            db.add(
                User(
                    id=1,
                    username="testuser",
                    email="test@example.com",
                    hashed_password=hash_password("testpass123"),
                )
            )
            db.commit()
