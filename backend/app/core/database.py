import logging
from functools import partial

from tortoise.contrib.fastapi import RegisterTortoise

from app.core.settings import settings

logger = logging.getLogger(__name__)

MODEL_MODULES = [
    "app.accidents.models",
    "app.accidents.lookup_tables",
]

TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    },
    "apps": {
        "models": {
            "models": [*MODEL_MODULES],
            "default_connection": "default",
            "migrations": "app.migrations",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

register_orm = partial(
    RegisterTortoise,
    config=TORTOISE_ORM,
)