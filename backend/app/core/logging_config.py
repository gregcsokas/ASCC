import logging
import logging.config

from app.core.settings import settings

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s - %(levelname)s - %(message)s",
            "use_colors": None,
        },
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "uvicorn_default": {
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "app_default": {
            "level": settings.LOG_LEVEL,
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["app_default"],
            "propagate": False,
        },
        "uvicorn": {
            "level": settings.LOG_LEVEL,
            "handlers": ["uvicorn_default"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": settings.LOG_LEVEL,
        },
        "uvicorn.access": {
            "level": settings.LOG_LEVEL,
            "handlers": [],
            "propagate": False,
        },
        "tortoise.db_client": {
            "level": settings.LOG_LEVEL,
            "handlers": ["app_default"],
            "propagate": False,
        },
    },
}

def setup_logging() -> logging.Logger:
    """Configure logging for the application."""

    logging.config.dictConfig(LOGGING_CONFIG)
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)

    return root_logger

logger = setup_logging()