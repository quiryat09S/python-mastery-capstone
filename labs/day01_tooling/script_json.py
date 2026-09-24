import json
from pathlib import Path


def cargar_y_procesar_datos(ruta_archivo: Path) -> list[dict]:
    """Lee un archivo JSON, filtra elementos activos y calcula el precio total

    manejando errores de formato de forma segura.
    """
    if not ruta_archivo.exists():
        raise FileNotFoundError(f"El archivo {ruta_archivo} no existe.")

    try:
        with open(ruta_archivo, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except json.JSONDecodeError as err:
        print(f"Error al parsear el archivo JSON: {err}")
        return []

    productos_validos = []
    for item in datos:
        try:
            if not item.get("activo"):
                continue

            precio = float(item["precio"])
            productos_validos.append(
                {"id": item["id"], "nombre": item["nombre"], "precio": precio}
            )
        except (KeyError, ValueError) as err:
            print(
                "Advertencia: Registro omitido por datos inválidos "
                f"({item}): {err}"
            )

    return productos_validos


if __name__ == "__main__":
    ruta = Path(__file__).parent / "datos.json"
    try:
        resultado = cargar_y_procesar_datos(ruta)
        print(f"\nProductos procesados correctamente: {resultado}")
    except FileNotFoundError as e:
        print(f"Error con el archivo especificado: {e}")
