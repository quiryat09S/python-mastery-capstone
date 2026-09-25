from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class OrderModel(Base):
    __tablename__ = "solid_orders"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    customer: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    total: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
