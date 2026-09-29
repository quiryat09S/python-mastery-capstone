FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /build

RUN pip install --no-cache-dir \
    "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock ./

RUN poetry install \
    --only main \
    --no-root

COPY labs ./labs

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.14/site-packages \
    /usr/local/lib/python3.14/site-packages

COPY --from=builder /usr/local/bin \
    /usr/local/bin

COPY --from=builder /build/labs ./labs

RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "labs.day09_fast_api.main:app", "--host", "0.0.0.0", "--port", "8000"]