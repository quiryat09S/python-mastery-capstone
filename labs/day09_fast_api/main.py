import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .auth import hash_password
from .database import SessionLocal, engine
from .models import Base, User
from .routers.auth import router as auth_router
from .routers.orders import router as orders_router

app = FastAPI(
    title="Orders API",
    description="API para gestionar órdenes",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    response = await call_next(request)

    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.6f}"

    return response


Base.metadata.create_all(bind=engine)


def ensure_user_exists() -> None:
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


ensure_user_exists()


app.include_router(auth_router)
app.include_router(orders_router)


@app.get("/")
def root():
    return {
        "message": "Orders API funcionando",
    }
