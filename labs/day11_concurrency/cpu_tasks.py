from collections.abc import Iterable
from concurrent.futures import ProcessPoolExecutor


def sum_of_squares(limit: int) -> int:
    if limit < 0:
        raise ValueError("limit debe ser mayor o igual que cero")

    return sum(number * number for number in range(limit))


def calculate_parallel(
    limits: Iterable[int],
    workers: int | None = None,
) -> list[int]:
    with ProcessPoolExecutor(
        max_workers=workers,
    ) as executor:
        return list(executor.map(sum_of_squares, limits))
