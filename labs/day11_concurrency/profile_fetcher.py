import asyncio
import cProfile
import pstats

import httpx

from .fetcher import fetch_async


def create_mock_transport() -> httpx.MockTransport:
    async def mock_handler(
        request: httpx.Request,
    ) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={
                "url": str(request.url),
                "status": "ok",
            },
            request=request,
        )

    return httpx.MockTransport(mock_handler)


async def run_profiled_fetch(
    urls: list[str],
) -> None:
    transport = create_mock_transport()

    await fetch_async(
        urls,
        transport=transport,
    )


def profile_async_fetch(
    urls: list[str],
) -> None:
    profiler = cProfile.Profile()

    profiler.enable()

    asyncio.run(run_profiled_fetch(urls))

    profiler.disable()

    stats = pstats.Stats(profiler)
    stats.sort_stats("cumulative")
    stats.print_stats(20)


if __name__ == "__main__":
    profile_async_fetch(
        [
            "https://example.com/1",
            "https://example.com/2",
        ]
    )
