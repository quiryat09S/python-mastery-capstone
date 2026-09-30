# mypy: disable-error-code=attr-defined
# mypy: disable-error-code=name-defined

import grpc

from .generated import orders_pb2, orders_pb2_grpc


def create_order(
    host: str = "localhost:50051",
) -> object:
    with grpc.insecure_channel(host) as channel:
        stub = orders_pb2_grpc.OrdersServiceStub(channel)

        return stub.CreateOrder(
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


if __name__ == "__main__":
    response = create_order()
    print(response)
