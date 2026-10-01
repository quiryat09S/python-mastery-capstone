from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...application.dto import CreateOrderInput, CreateOrderItemInput
from ...application.order_commands import CancelOrder, DeleteOrder
from ...application.order_queries import GetOrder, ListOrders
from ...application.use_cases import CreateOrder
from ...domain.exceptions import InvalidOrderStateError, OrderNotFoundError
from ...infrastructure.models import UserModel
from ..dependencies import (
    get_current_user,
    get_db,
    provide_cancel_order,
    provide_create_order,
    provide_delete_order,
    provide_get_order,
    provide_list_orders,
)
from ..presenters import present_order
from ..schemas import CreateOrderRequest, OrderResponse

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    data: CreateOrderRequest,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    use_case: CreateOrder = provide_create_order(db)

    result = use_case.execute(
        CreateOrderInput(
            user_id=current_user.id,
            items=tuple(
                CreateOrderItemInput(
                    product_name=item.product_name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in data.items
            ),
        )
    )

    return present_order(result)


@router.get(
    "/",
    response_model=list[OrderResponse],
)
def list_orders(
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    use_case: ListOrders = provide_list_orders(db)

    return [
        present_order(order) for order in use_case.execute(current_user.id)
    ]


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    use_case: GetOrder = provide_get_order(db)

    order = use_case.execute(
        order_id=order_id,
        user_id=current_user.id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order no encontrada",
        )

    return present_order(order)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
)
def cancel_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    use_case: CancelOrder = provide_cancel_order(db)

    try:
        order = use_case.execute(
            order_id=order_id,
            user_id=current_user.id,
        )
    except InvalidOrderStateError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return present_order(order)


@router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_order(
    order_id: int,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    use_case: DeleteOrder = provide_delete_order(db)

    try:
        use_case.execute(
            order_id=order_id,
            user_id=current_user.id,
        )
    except OrderNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return None
