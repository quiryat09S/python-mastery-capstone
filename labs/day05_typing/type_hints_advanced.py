from collections.abc import Sequence
from typing import Literal, Protocol, runtime_checkable

# Tipos definidos mediante alias y Literal
EstadoNotificacion = Literal["pendiente", "completado", "fallido"]
Prioridad = Literal["baja", "media", "alta"]


# Protocolo (Interface implícita/Structural Subtyping)
@runtime_checkable
class CanalNotificacion(Protocol):
    def enviar(self, mensaje: str, destinatario: str) -> bool:
        """Define el contrato que debe cumplir el canal."""
        ...


# Implementación 1: No hereda explícitamente de CanalNotificacion
class ServicioEmail:
    def __init__(self, servidor_smtp: str) -> None:
        self.servidor_smtp = servidor_smtp

    def enviar(self, mensaje: str, destinatario: str) -> bool:
        print(
            f" [Email via {self.servidor_smtp}] "
            f"Para: {destinatario} | Msg: {mensaje}"
        )
        return True


# Implementación 2: Tampoco hereda, pero cumple la firma exacta
class ServicioSMS:
    def enviar(self, mensaje: str, destinatario: str) -> bool:
        print(f" [SMS] Para: {destinatario} | Msg: {mensaje}")
        return True


# Depende exclusivamente del protocolo y usa unión moderna (|)
def notificar_usuarios(
    canal: CanalNotificacion,
    destinatarios: Sequence[str],
    mensaje: str,
    prioridad: Prioridad | None = None,
) -> dict[str, EstadoNotificacion]:
    """Envía notificaciones desacopladas mediante DIP."""
    resultados: dict[str, EstadoNotificacion] = {}

    prefix = f"[{prioridad.upper()}] " if prioridad else ""
    mensaje_final = f"{prefix}{mensaje}"

    for usuario in destinatarios:
        exito = canal.enviar(mensaje_final, usuario)
        resultados[usuario] = "completado" if exito else "fallido"

    return resultados


if __name__ == "__main__":
    email_service = ServicioEmail(servidor_smtp="smtp.empresa.com")
    sms_service = ServicioSMS()

    lista_usuarios: list[str] = ["admin@empresa.com", "devops@empresa.com"]

    print("--- 1. Envió con ServicioEmail ---")
    res_email = notificar_usuarios(
        canal=email_service,
        destinatarios=lista_usuarios,
        mensaje="Despliegue exitoso en Producción",
        prioridad="alta",
    )
    print("Resultado Email:", res_email)

    print("\n--- 2. Envió con ServicioSMS ---")
    res_sms = notificar_usuarios(
        canal=sms_service,
        destinatarios=["+525512345678"],
        mensaje="Alerta de CPU elevada",
    )
    print("Resultado SMS:", res_sms)

    # Verificación en tiempo de ejecución con @runtime_checkable
    print(
        f"\n¿ServicioEmail cumple CanalNotificacion?: "
        f"{isinstance(email_service, CanalNotificacion)}"
    )
