from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ...infrastructure.models import UserModel
from ...infrastructure.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from ..dependencies import get_db
from ..schemas import TokenResponse, UserCreateRequest, UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: UserCreateRequest,
    db: Session = Depends(get_db),
):
    existing_user = (
        db.query(UserModel)
        .filter(
            (UserModel.username == data.username)
            | (UserModel.email == str(data.email))
        )
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya existe",
        )

    user = UserModel(
        username=data.username,
        email=str(data.email),
        hashed_password=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(UserModel)
        .filter(UserModel.username == form_data.username)
        .first()
    )

    if user is None or not verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }
