from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

# --- 1. Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("http_resilient_client")


# --- 2. DTOs de Resultado ---
@dataclass
class DownloadResult:
    url: str
    destination_path: Path
    bytes_downloaded: int
    duration_seconds: float


# --- 3. Cliente HTTP Resiliente ---
class ResilientHTTPClient:
    """Cliente HTTP construido sobre HTTPX con soporte de reintentos,

    timeouts estrictos y descargas eficientes por streaming.
    """

    def __init__(
        self,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 1.5,
    ) -> None:
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        # Configuración granular de timeouts
        self.timeout = httpx.Timeout(
            timeout_seconds,
            connect=5.0,
            read=timeout_seconds,
        )

    def download_file_stream(
        self,
        url: str,
        destination: Path,
        chunk_size: int = 8192,
    ) -> DownloadResult:
        """Descarga un recurso mediante streaming directo a disco,

        aplicando reintentos con backoff exponencial.
        """
        destination.parent.mkdir(parents=True, exist_ok=True)
        start_time = time.perf_counter()
        attempt = 0

        while attempt <= self.max_retries:
            attempt += 1
            try:
                logger.info(
                    "Iniciando solicitud HTTP (Intento %d/%d) a: %s",
                    attempt,
                    self.max_retries + 1,
                    url,
                )

                bytes_count = 0
                # SIM117: Combinación de contexts de `with`
                with (
                    httpx.Client(timeout=self.timeout, follow_redirects=True) as client,
                    client.stream("GET", url) as response,
                ):
                    response.raise_for_status()

                    with destination.open("wb") as file_out:
                        for chunk in response.iter_bytes(chunk_size=chunk_size):
                            file_out.write(chunk)
                            bytes_count += len(chunk)

                duration = time.perf_counter() - start_time
                logger.info(
                    "Descarga completada exitosamente. Total: %d bytes en %.2fs.",
                    bytes_count,
                    duration,
                )

                return DownloadResult(
                    url=url,
                    destination_path=destination,
                    bytes_downloaded=bytes_count,
                    duration_seconds=round(duration, 2),
                )

            except (httpx.TimeoutException, httpx.NetworkError) as err:
                logger.warning(
                    "Fallo de red o timeout [%s]: %s", type(err).__name__, err
                )
            except httpx.HTTPStatusError as err:
                logger.error(
                    "Error de respuesta HTTP %d desde el servidor: %s",
                    err.response.status_code,
                    err,
                )
                # Si es un error del cliente (4xx), no reintentamos
                if 400 <= err.response.status_code < 500:
                    raise

            if attempt <= self.max_retries:
                sleep_time = self.backoff_factor**attempt
                logger.info("Reintentando en %.1f segundos...", sleep_time)
                time.sleep(sleep_time)

        raise RuntimeError(
            f"No se pudo completar la descarga desde {url} tras {self.max_retries + 1} intentos."
        )


# --- 4. Demostración de Uso ---
if __name__ == "__main__":
    download_dir = Path(__file__).parent / "downloads"
    output_filepath = download_dir / "sample_data.bin"

    # URL pública de prueba para transmisión de bytes
    target_url = "https://httpbin.org/bytes/50000"

    cliente = ResilientHTTPClient(
        timeout_seconds=5.0, max_retries=2, backoff_factor=1.5
    )

    try:
        resultado = cliente.download_file_stream(
            url=target_url, destination=output_filepath
        )
        print(f"\nReporte de Descarga: {resultado}")
    # BLE001: Captura explícita de las excepciones esperadas
    except (httpx.HTTPError, RuntimeError) as exc:
        logger.error("La operación falló definitivamente: %s", exc)
