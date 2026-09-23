from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from labs.day08_orm_alembic.database import SessionLocal, init_db
from labs.day08_orm_alembic.models import Order, OrderItem, User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orm_demo")


def crear_usuario_con_orden(
    session: Session,
    username: str,
    email: str,
    productos: list[tuple[str, int, Decimal]],
) -> User:
    """Crea un usuario, una orden y sus items en una transacción."""

    user = User(
        username=username,
        email=email,
    )

    order = Order(
        status="PAID",
    )

    for nombre, cantidad, precio in productos:
        item = OrderItem(
            product_name=nombre,
            quantity=cantidad,
            unit_price=precio,
        )

        order.items.append(item)

    user.orders.append(order)

    # Transacción explícita
    with session.begin():
        session.add(user)

    session.refresh(user)

    logger.info(
        "Usuario '%s' y Orden #%d creados con éxito.",
        user.username,
        order.id,
    )

    return user


def consultar_ordenes_usuario(
    session: Session,
    username: str,
) -> list[Order]:
    """Obtiene las órdenes de un usuario."""

    stmt = select(Order).join(User).where(User.username == username)

    return list(session.scalars(stmt).all())


def actualizar_estado_orden(
    session: Session,
    order_id: int,
    nuevo_estado: str,
) -> None:
    """Actualiza el estado de una orden dentro de una transacción."""

    order = session.get(Order, order_id)

    if order is None:
        logger.warning(
            "No se encontró la Orden #%d.",
            order_id,
        )
        return

    with session.begin():
        order.status = nuevo_estado

    logger.info(
        "Estado de la Orden #%d actualizado a '%s'.",
        order_id,
        nuevo_estado,
    )


def eliminar_usuario(
    session: Session,
    user_id: int,
) -> None:
    """Elimina un usuario y sus órdenes mediante cascade."""

    user = session.get(User, user_id)

    if user is None:
        logger.warning(
            "No se encontró el Usuario ID %d.",
            user_id,
        )
        return

    with session.begin():
        session.delete(user)

    logger.info(
        "Usuario ID %d y sus órdenes han sido eliminados.",
        user_id,
    )


if __name__ == "__main__":
    # Crear las tablas en SQLite en memoria
    init_db()

    with SessionLocal() as db:

        # -------------------------
        # CREATE
        # -------------------------
        usuario = crear_usuario_con_orden(
            session=db,
            username="dev_python",
            email="dev@ejemplo.com",
            productos=[
                ("Teclado Mecánico", 1, Decimal("120.50")),
                ("Mouse Ergonómico", 2, Decimal("45.00")),
            ],
        )

        # -------------------------
        # READ
        # -------------------------
        ordenes = consultar_ordenes_usuario(
            db,
            "dev_python",
        )

        for orden in ordenes:
            print(f"\nOrden ID: {orden.id} | " f"Estado: {orden.status}")

            for item in orden.items:
                print(
                    f" - {item.product_name} "
                    f"x{item.quantity} = "
                    f"${item.unit_price}"
                )

        # -------------------------
        # UPDATE
        # -------------------------
        if ordenes:
            actualizar_estado_orden(
                db,
                ordenes[0].id,
                "SHIPPED",
            )

        # -------------------------
        # DELETE
        # -------------------------
        eliminar_usuario(
            db,
            usuario.id,
        )
