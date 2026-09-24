from datetime import datetime
from decimal import Decimal
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderStatus(StrEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"


class OrderItemCreate(BaseModel):
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


class OrderCreate(BaseModel):
    status: OrderStatus = OrderStatus.PENDING
    items: list[OrderItemCreate] = Field(
        min_length=1,
    )


class OrderItemResponse(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: str
    created_at: datetime
    items: list[OrderItemResponse]

    model_config = ConfigDict(
        from_attributes=True,
    )


class OrderUpdate(BaseModel):
    status: OrderStatus


class UserCreate(BaseModel):
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
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
