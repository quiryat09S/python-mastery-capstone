def send_order_cancelled_notification(
    username: str,
    order_id: int,
) -> None:
    print(f"Notificación enviada a {username} " f"para la orden {order_id}")
