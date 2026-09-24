from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ...day10_testing_tdd.notifications import (
    send_order_cancelled_notification,
)
from ..database import get_db
from ..dependencies import get_current_user
from ..models import Order, OrderItem, User
from ..schemas import OrderCreate, OrderResponse, OrderUpdate

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = Order(
        status=order_data.status,
        user_id=current_user.id,
    )

    for item_data in order_data.items:
        order.items.append(
            OrderItem(
                product_name=item_data.product_name,
                quantity=item_data.quantity,
                unit_price=item_data.unit_price,
            )
        )

    db.add(order)
    db.commit()
    db.refresh(order)

    return order


# Endpoint agregado
@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancelar_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )

    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order no encontrada",
        )

    if order.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se pueden cancelar órdenes PENDING",
        )

    order.status = "CANCELLED"

    db.commit()
    db.refresh(order)

    send_order_cancelled_notification(
        username=current_user.username,
        order_id=order.id,
    )
    return order


@router.get(
    "/",
    response_model=list[OrderResponse],
)
def listar_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == current_user.id)
    )

    return list(db.scalars(statement).all())


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def obtener_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )

    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order no encontrada",
        )

    return order


@router.put(
    "/{order_id}",
    response_model=OrderResponse,
)
def actualizar_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id,
        )
    )

    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order no encontrada",
        )

    order.status = order_data.status
    db.commit()
    db.refresh(order)

    return order


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Order).where(
        Order.id == order_id,
        Order.user_id == current_user.id,
    )

    order = db.scalars(statement).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order no encontrada",
        )

    db.delete(order)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
