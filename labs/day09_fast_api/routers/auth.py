from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import create_access_token, hash_password, verify_password
from ..database import get_db
from ..models import User
from ..schemas import TokenResponse, UserCreate, UserResponse

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
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    username_exists = User.username == user_data.username
    email_exists = User.email == user_data.email

    existing_user = db.scalar(
        select(User).where(username_exists | email_exists)
    )
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario o email ya existe",
        )

    user = User(
        username=user_data.username,
        email=str(user_data.email),
        hashed_password=hash_password(user_data.password),
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
    user = db.scalar(select(User).where(User.username == form_data.username))

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

    access_token = create_access_token(user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
