import logging
import time
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .domain.exceptions import DomainError
from .infrastructure.logging_config import configure_logging
from .presentation.routers.auth import router as auth_router
from .presentation.routers.orders import router as orders_router

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Final Orders API",
    description="Orders service with clean architecture",
    version="1.0.0",
)


app.include_router(auth_router)
app.include_router(orders_router)


@app.middleware("http")
async def observability_middleware(
    request: Request,
    call_next,
):
    start_time = time.perf_counter()

    correlation_id = request.headers.get(
        "X-Correlation-ID",
        str(uuid4()),
    )

    response = await call_next(request)

    duration = time.perf_counter() - start_time

    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time"] = f"{duration:.6f}"

    logger.info(
        "request completed method=%s path=%s status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )

    return response


@app.exception_handler(DomainError)
async def handle_domain_error(
    request: Request,
    exc: DomainError,
):
    logger.warning(
        "domain error path=%s detail=%s",
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc),
        },
    )


@app.exception_handler(Exception)
async def handle_unexpected_error(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "unexpected error path=%s",
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
        },
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
    }


@app.get("/ready")
def ready():
    return {
        "status": "ready",
    }
