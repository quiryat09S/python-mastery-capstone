import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from functools import wraps
from typing import Any


# 1. Decorador con *args y **kwargs (Lógica de reintentos)
def reintentar(intentos_max: int = 3, retraso: float = 0.5) -> Callable:
    """Decorador que reintenta ejecutar una función si lanza una excepción."""

    def decorador(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for intento in range(1, intentos_max + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as err:
                    print(
                        f"[Intento {intento}/{intentos_max}] Error en {func.__name__}: {err}"
                    )
                    if intento == intentos_max:
                        raise
                    time.sleep(retraso)

        return wrapper

    return decorador


# 2. Context Manager personalizado
@contextmanager
def medir_tiempo(etiqueta: str) -> Generator[None]:
    """Context manager para medir el tiempo de ejecución de un bloque de código."""
    inicio = time.perf_counter()
    try:
        yield
    finally:
        fin = time.perf_counter()
        print(f"⏱️ [{etiqueta}] Tiempo transcurrido: {fin - inicio:.4f} segundos")


# 3. Generador eficiente en memoria
def procesar_stream_datos(total_registros: int) -> Generator[dict]:
    """Genera datos secuencialmente usando yield sin cargar todo en RAM."""
    for i in range(1, total_registros + 1):
        yield {
            "id": i,
            "sku": f"PROD-{i:03d}",
            "monto": float(i * 10.5),
            "activo": i % 2 == 0,
        }


# Simulación de función inestable decorada
@reintentar(intentos_max=2, retraso=0.2)
def operacion_riesgosa(datos: dict) -> dict:
    if not datos["activo"]:
        raise ValueError("El registro no está activo")
    return {"id": datos["id"], "procesado": True}


if __name__ == "__main__":
    print("--- 1. Pruebas de Generadores y Comprensiones ---")
    # Generator expression para filtrar elementos sin evaluar toda la lista
    stream = procesar_stream_datos(5)
    activos = (item for item in stream if item["activo"])

    with medir_tiempo("Procesamiento de Stream"):
        for registro in activos:
            try:
                res = operacion_riesgosa(registro)
                print(f"Éxito: {res}")
            except ValueError as e:
                print(f"Fallo definitivo: {e}")
