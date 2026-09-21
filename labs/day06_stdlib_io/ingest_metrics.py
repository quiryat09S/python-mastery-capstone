from __future__ import annotations

import csv
import json
import logging
import logging.config
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

# --- 1. Configuración de Logging Estructurado ---
LOGGING_CONFIG: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structured": {
            "format": "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "structured",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app_ingest.log",
            "level": "DEBUG",
            "formatter": "structured",
            "encoding": "utf-8",
        },
    },
    "root": {
        "level": "DEBUG",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("sales_processor")


# --- 2. Entidades de Dominio y DTOs ---
@dataclass
class Transaction:
    transaction_id: str
    product_category: str
    amount: float
    timestamp: datetime


@dataclass
class CategoryMetric:
    category: str
    total_sales: float
    transaction_count: int
    average_ticket: float


@dataclass
class MetricsReport:
    generated_at: str
    total_revenue: float
    total_transactions: int
    categories: list[CategoryMetric]


# --- 3. Componentes de Ingesta y Procesamiento ---
class SalesIngestor:
    """Puerto de Lectura/E/S de datos CSV."""

    @staticmethod
    def read_csv(file_path: Path) -> list[Transaction]:
        if not file_path.exists():
            logger.error("El archivo especificado no existe: %s", file_path.resolve())
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        transactions: list[Transaction] = []
        logger.info("Iniciando la lectura del archivo CSV: %s", file_path.name)

        with file_path.open(mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row_num, row in enumerate(reader, start=2):
                try:
                    tx = Transaction(
                        transaction_id=row["transaction_id"],
                        product_category=row["category"],
                        amount=float(row["amount"]),
                        timestamp=datetime.fromisoformat(row["timestamp"]),
                    )
                    transactions.append(tx)
                except (KeyError, ValueError) as err:
                    logger.warning(
                        "Fila %d omitida por formato inválido: %s. Error: %s",
                        row_num,
                        row,
                        err,
                    )

        logger.info(
            "Ingesta completada. %d transacciones válidas procesadas.",
            len(transactions),
        )
        return transactions


class MetricsCalculator:
    """Lógica de Dominio para agregación de métricas."""

    @staticmethod
    def calculate(transactions: list[Transaction]) -> MetricsReport:
        logger.debug("Calculando métricas para %d transacciones...", len(transactions))

        if not transactions:
            return MetricsReport(
                generated_at=datetime.now(UTC).isoformat(),
                total_revenue=0.0,
                total_transactions=0,
                categories=[],
            )

        category_totals: dict[str, float] = {}
        category_counts: dict[str, int] = {}
        total_revenue = 0.0

        for tx in transactions:
            total_revenue += tx.amount
            category_totals[tx.product_category] = (
                category_totals.get(tx.product_category, 0.0) + tx.amount
            )
            category_counts[tx.product_category] = (
                category_counts.get(tx.product_category, 0) + 1
            )

        category_metrics: list[CategoryMetric] = []
        for cat, total in category_totals.items():
            count = category_counts[cat]
            avg = round(total / count, 2)
            category_metrics.append(
                CategoryMetric(
                    category=cat,
                    total_sales=round(total, 2),
                    transaction_count=count,
                    average_ticket=avg,
                )
            )

        return MetricsReport(
            generated_at=datetime.now(UTC).isoformat(),
            total_revenue=round(total_revenue, 2),
            total_transactions=len(transactions),
            categories=category_metrics,
        )


class JSONExporter:
    """Puerto de Salida de E/S de datos JSON."""

    @staticmethod
    def export(report: MetricsReport, output_path: Path) -> None:
        logger.info("Exportando reporte de métricas a: %s", output_path.resolve())
        report_dict = asdict(report)

        # Garantizar que el directorio padre exista
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open(mode="w", encoding="utf-8") as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        logger.info("Exportación exitosa.")


# --- 4. Flujo Principal de Demostración ---
def preparar_datos_demostracion(csv_path: Path) -> None:
    """Crea un CSV de datos de prueba usando pathlib."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    content = (
        "transaction_id,category,amount,timestamp\n"
        "TX1001,Electronics,299.99,2026-09-20T10:15:00+00:00\n"
        "TX1002,Books,15.50,2026-09-20T11:30:00+00:00\n"
        "TX1003,Electronics,120.00,2026-09-20T12:00:00+00:00\n"
        "TX1004,Home,45.00,2026-09-20T14:22:00+00:00\n"
        "TX1005,Books,CORRUPT_DATA,2026-09-20T15:00:00+00:00\n"  # Fila corrupta intencional
    )
    csv_path.write_text(content, encoding="utf-8")
    logger.debug("Archivo de prueba generado en: %s", csv_path)


if __name__ == "__main__":
    base_dir = Path(__file__).parent / "data"
    input_file = base_dir / "raw_sales.csv"
    output_file = base_dir / "metrics_report.json"

    # 1. Preparar archivo de entrada
    preparar_datos_demostracion(input_file)

    # 2. Ingesta CSV
    transacciones = SalesIngestor.read_csv(input_file)

    # 3. Procesamiento de Dominio
    reporte = MetricsCalculator.calculate(transacciones)

    # 4. Exportación JSON
    JSONExporter.export(reporte, output_file)

    print("\nProceso finalizado. Revisa 'app_ingest.log' para ver el log estructurado.")
