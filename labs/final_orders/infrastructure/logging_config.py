import logging
import logging.config


def configure_logging() -> None:
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "structured": {
                    "format": (
                        "%(asctime)s "
                        "%(levelname)s "
                        "%(name)s "
                        "%(message)s"
                    ),
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "structured",
                },
            },
            "root": {
                "level": "INFO",
                "handlers": ["console"],
            },
        }
    )
