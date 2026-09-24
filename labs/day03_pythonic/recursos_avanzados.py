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
                        f"[Intento {intento}/{intentos_max}] "
                        f"Error en {func.__name__}: {err}"
                    )
                    if intento == intentos_max:
                        raise

                    espera = retraso * (
                        2 ** (intento - 1)
                    )  # Modificación para backoff.
                    print(f"Reintentando en {espera:.2f} segundos...")
                    time.sleep(espera)

        return wrapper

    return decorador


# 2. Context Manager personalizado
@contextmanager
def medir_tiempo(etiqueta: str) -> Generator[None]:
    """Mide el tiempo de ejecución de un bloque de código."""
    inicio = time.perf_counter()
    try:
        yield
    finally:
        fin = time.perf_counter()
        print(
            f" [{etiqueta}] Tiempo transcurrido: {fin - inicio:.4f} segundos"
        )


# 3. Generador eficiente en memoria
def procesar_lotes_datos(
    total_registros: int, tamano_lote: int = 2
) -> Generator[list[dict]]:

    lote = []

    for i in range(1, total_registros + 1):

        lote.append(
            {
                "id": i,
                "sku": f"PROD-{i:03d}",
                "monto": float(i * 10.5),
                "activo": i % 2 == 0,
            }
        )

        if len(lote) == tamano_lote:
            yield lote
            lote = []

    # Entregar el último lote aunque esté incompleto
    if lote:
        yield lote


# Simulación de función inestable decorada
@reintentar(intentos_max=2, retraso=0.2)
def operacion_riesgosa(datos: dict) -> dict:
    if not datos["activo"]:
        raise ValueError("El registro no está activo")
    return {"id": datos["id"], "procesado": True}


if __name__ == "__main__":
    print("--- 1. Pruebas de Generadores y Comprensiones ---")
    # Generator expression para filtrar elementos sin evaluar toda la lista
    stream = procesar_lotes_datos(5, tamano_lote=2)

    with medir_tiempo("Procesamiento de Stream"):

        for lote in stream:

            for registro in lote:

                if registro["activo"]:
                    try:
                        res = operacion_riesgosa(registro)
                        print(f"Éxito: {res}")
                    except ValueError as e:
                        print(f"Fallo definitivo: {e}")
