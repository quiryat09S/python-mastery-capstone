import asyncio
import time
from unittest.mock import AsyncMock, patch

import httpx

from labs.day11_concurrency.fetcher import fetch_async, fetch_sync


def test_async_fetch_is_faster_than_sync_fetch():
    urls = [f"https://example.com/{index}" for index in range(4)]

    def fake_sync_get(
        self,
        url,
    ):
        time.sleep(0.02)

        return httpx.Response(
            status_code=200,
            request=httpx.Request(
                "GET",
                url,
            ),
        )

    async def fake_async_get(url):
        await asyncio.sleep(0.02)

        return httpx.Response(
            status_code=200,
            request=httpx.Request(
                "GET",
                url,
            ),
        )

    with patch.object(
        httpx.Client,
        "get",
        new=fake_sync_get,
    ):
        sync_start = time.perf_counter()
        sync_responses = fetch_sync(urls)
        sync_duration = time.perf_counter() - sync_start

    with patch.object(
        httpx.AsyncClient,
        "get",
        new=AsyncMock(
            side_effect=fake_async_get,
        ),
    ):
        async_start = time.perf_counter()
        async_responses = asyncio.run(
            fetch_async(
                urls,
                concurrency=4,
            )
        )
        async_duration = time.perf_counter() - async_start

    assert len(sync_responses) == len(urls)
    assert len(async_responses) == len(urls)
    assert async_duration < sync_duration
