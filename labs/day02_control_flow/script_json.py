import json
import re
from pathlib import Path

# Expresión regular para validar el código SKU (3 letras - 3 números)
PATRON_SKU = r"^[A-Z]{3}-\d{3}$"


class ErrorDatoInvalido(Exception):
    """Excepción para errores en campos del JSON."""


def procesar_registro(item: dict) -> dict:
    """Valida cada registro con Pattern Matching y Expresiones Regulares."""
    match item:
        case {
            "sku": str(sku),
            "nombre": str(nombre),
            "precio": precio_raw,
            "activo": True,
        }:
            if not re.match(PATRON_SKU, sku):
                raise ErrorDatoInvalido(
                    f"SKU '{sku}' no cumple el formato 'AAA-000'"
                )

            try:
                precio = float(precio_raw)
                if precio <= 0:
                    raise ValueError("El precio debe ser positivo")
            except (ValueError, TypeError) as exc:
                raise ErrorDatoInvalido(
                    f"Precio inválido ({precio_raw}): {exc}"
                ) from exc

            return {"sku": sku, "nombre": nombre, "precio": precio}

        case {"activo": False}:
            raise ErrorDatoInvalido("Registro inactivo")

        case _:
            raise ErrorDatoInvalido(
                "Estructura de registro no compatible o incompleta"
            )


def cargar_y_procesar_datos(ruta_archivo: Path) -> list[dict]:
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")

    with open(ruta_archivo, encoding="utf-8") as archivo:
        datos = json.load(archivo)

    productos_validos = []
    for item in datos:
        try:
            valido = procesar_registro(item)
            productos_validos.append(valido)
        except ErrorDatoInvalido as err:
            print(f"Registro omitido: {err}")

    return productos_validos


if __name__ == "__main__":
    ruta = Path(__file__).parent / "datos.json"
    try:
        resultado = cargar_y_procesar_datos(ruta)
        print(f"\nProductos procesados correctamente: {resultado}")
    except FileNotFoundError as e:
        print(f"Error con el archivo especificado: {e}")
