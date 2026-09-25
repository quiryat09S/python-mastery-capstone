import asyncio
from collections.abc import Iterable

import httpx


def fetch_sync(
    urls: Iterable[str],
    timeout: float = 10.0,
) -> list[httpx.Response]:
    responses = []

    with httpx.Client(timeout=timeout) as client:
        for url in urls:
            response = client.get(url)
            response.raise_for_status()
            responses.append(response)

    return responses


async def fetch_one(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
) -> httpx.Response:
    async with semaphore:
        response = await client.get(url)
        response.raise_for_status()
        return response


async def fetch_async(
    urls: Iterable[str],
    concurrency: int = 5,
    timeout: float = 10.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> list[httpx.Response]:
    if concurrency < 1:
        raise ValueError("concurrency debe ser mayor que cero")

    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(
        timeout=timeout,
        transport=transport,
    ) as client:
        tasks = [fetch_one(client, url, semaphore) for url in urls]

        return await asyncio.gather(*tasks)
