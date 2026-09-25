import asyncio
import timeit
from collections.abc import Callable

from .fetcher import fetch_async, fetch_sync


def measure_sync(
    urls: list[str],
) -> float:
    return timeit.timeit(
        lambda: fetch_sync(urls),
        number=1,
    )


def measure_async(
    urls: list[str],
) -> float:
    return timeit.timeit(
        lambda: asyncio.run(fetch_async(urls)),
        number=1,
    )


def compare_fetchers(
    urls: list[str],
) -> dict[str, float]:
    sync_duration = measure_sync(urls)
    async_duration = measure_async(urls)

    return {
        "sync_seconds": sync_duration,
        "async_seconds": async_duration,
        "speedup": sync_duration / async_duration,
    }


def run_benchmark(
    function: Callable[[], object],
    repetitions: int = 3,
) -> float:
    if repetitions < 1:
        raise ValueError("repetitions debe ser mayor que cero")

    return timeit.timeit(
        function,
        number=repetitions,
    )
