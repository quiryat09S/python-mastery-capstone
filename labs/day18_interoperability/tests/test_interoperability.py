import json
from concurrent import futures
from unittest.mock import Mock

import grpc

from labs.day18_interoperability.generated import orders_pb2, orders_pb2_grpc
from labs.day18_interoperability.grpc_server import OrdersService
from labs.day18_interoperability.publisher import (
    OrderCreated,
    RedisOrderPublisher,
)


def test_redis_publisher():
    client = Mock()
    publisher = RedisOrderPublisher(client)

    event = OrderCreated(
        order_id=1,
        customer_id=10,
        status="PENDING",
        total=100.0,
    )

    publisher.publish(event)

    client.publish.assert_called_once()

    channel, payload = client.publish.call_args.args

    assert channel == "orders.created"

    assert json.loads(payload) == {
        "order_id": 1,
        "customer_id": 10,
        "status": "PENDING",
        "total": 100.0,
    }


def test_order_proto_contract():
    request = orders_pb2.CreateOrderRequest(
        customer_id=10,
        items=[
            orders_pb2.OrderItem(
                product_name="Keyboard",
                quantity=2,
                unit_price=50.0,
            )
        ],
    )

    assert request.customer_id == 10
    assert len(request.items) == 1
    assert request.items[0].product_name == "Keyboard"
    assert request.items[0].quantity == 2
    assert request.items[0].unit_price == 50.0


def test_grpc_create_order():
    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=2,
        )
    )

    orders_pb2_grpc.add_OrdersServiceServicer_to_server(
        OrdersService(),
        server,
    )

    port = server.add_insecure_port("localhost:0")

    server.start()

    try:
        with grpc.insecure_channel(f"localhost:{port}") as channel:
            stub = orders_pb2_grpc.OrdersServiceStub(channel)

            response = stub.CreateOrder(
                orders_pb2.CreateOrderRequest(
                    customer_id=10,
                    items=[
                        orders_pb2.OrderItem(
                            product_name="Keyboard",
                            quantity=2,
                            unit_price=50.0,
                        )
                    ],
                )
            )

        assert response.order_id == 1
        assert response.customer_id == 10
        assert response.status == "PENDING"
        assert response.total == 100.0

    finally:
        server.stop(grace=0)
