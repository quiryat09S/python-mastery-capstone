import asyncio
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from labs.day11_concurrency.cpu_tasks import calculate_parallel, sum_of_squares
from labs.day11_concurrency.fetcher import fetch_async


def test_sum_of_squares():
    assert sum_of_squares(5) == 30


def test_sum_of_squares_rejects_negative_limit():
    with pytest.raises(ValueError):
        sum_of_squares(-1)


def test_calculate_parallel():
    result = calculate_parallel([5, 10])

    assert result == [30, 285]


# Prueba del semáforo
@pytest.mark.asyncio
async def test_fetch_async_respects_concurrency_limit():
    active_requests = 0
    max_active_requests = 0

    async def fake_fetch(url):
        nonlocal active_requests
        nonlocal max_active_requests

        active_requests += 1
        max_active_requests = max(
            max_active_requests,
            active_requests,
        )

        await asyncio.sleep(0.01)

        active_requests -= 1

        return httpx.Response(
            status_code=200,
            request=httpx.Request(
                "GET",
                url,
            ),
        )

    urls = [f"https://example.com/{index}" for index in range(6)]

    with patch.object(
        httpx.AsyncClient,
        "get",
        new=AsyncMock(side_effect=fake_fetch),
    ):
        responses = await fetch_async(
            urls,
            concurrency=2,
        )

    assert len(responses) == 6
    assert all(response.status_code == 200 for response in responses)
    assert max_active_requests <= 2


# prueba de validación de concurrencia
@pytest.mark.asyncio
async def test_fetch_async_rejects_invalid_concurrency():
    with pytest.raises(ValueError):
        await fetch_async(
            ["https://example.com"],
            concurrency=0,
        )
