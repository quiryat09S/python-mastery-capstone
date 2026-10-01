from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderItemRequest(BaseModel):
    product_name: str = Field(
        min_length=1,
        max_length=100,
    )
    quantity: int = Field(
        gt=0,
    )
    unit_price: Decimal = Field(
        gt=0,
        decimal_places=2,
        max_digits=10,
    )


class CreateOrderRequest(BaseModel):
    items: list[OrderItemRequest] = Field(
        min_length=1,
    )


class OrderResponse(BaseModel):
    id: int
    user_id: int
    total: Decimal
    status: str


class UserCreateRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
    )
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
