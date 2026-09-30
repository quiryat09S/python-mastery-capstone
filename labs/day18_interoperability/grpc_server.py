from concurrent import futures

import grpc

from .generated import orders_pb2, orders_pb2_grpc


class OrdersService(orders_pb2_grpc.OrdersServiceServicer):
    def CreateOrder(
        self,
        request,
        context,
    ):
        total = sum(item.quantity * item.unit_price for item in request.items)

        return orders_pb2.OrderResponse(
            order_id=1,
            customer_id=request.customer_id,
            status="PENDING",
            total=total,
        )

    def GetOrder(
        self,
        request,
        context,
    ):
        return orders_pb2.OrderResponse(
            order_id=request.order_id,
            customer_id=10,
            status="PENDING",
            total=100.0,
        )


def create_server() -> grpc.Server:
    server = grpc.server(
        futures.ThreadPoolExecutor(
            max_workers=4,
        )
    )

    orders_pb2_grpc.add_OrdersServiceServicer_to_server(
        OrdersService(),
        server,
    )

    server.add_insecure_port("[::]:50051")

    return server


def main() -> None:
    server = create_server()
    server.start()

    print("gRPC server running on port 50051")

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\nStopping gRPC server...")
        server.stop(grace=0)


if __name__ == "__main__":
    main()
