import time

from fastapi.testclient import TestClient

from labs.final_orders.main import app


def benchmark_health_requests(
    requests: int = 100,
) -> float:
    client = TestClient(app)

    start = time.perf_counter()

    for _ in range(requests):
        response = client.get("/health")
        assert response.status_code == 200

    return time.perf_counter() - start


if __name__ == "__main__":
    elapsed = benchmark_health_requests()

    print(f"100 requests completed in " f"{elapsed:.4f} seconds")
