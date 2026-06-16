import logging

from tortoise import Tortoise
from tortoise.log import logger as tortoise_logger

from app.core.settings import settings

logger = logging.getLogger(__name__)


TORTOISE_ORM = {
    "connections": {
        "default": f"postgres://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    },
    "apps": {
        "models": {
            "models": [],
            "default_connection": "default",
            "migrations": "app.migrations",
        },
    },
    "use_tz": True,
    "timezone": "UTC",
}

async def init_db() -> None:

    try:
        await Tortoise.init(
            config=TORTOISE_ORM,
            _enable_global_fallback=True
        )

        tortoise_logger.setLevel(settings.LOG_LEVEL)

        await Tortoise.generate_schemas()

        logger.info("Database initialization completed successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_db() -> None:
    logger.info("Closing database connections")
    await Tortoise.close_connections()
    logger.info("Database connections closed")