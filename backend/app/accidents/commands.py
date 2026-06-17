import asyncio
from typing import Any, Awaitable

import typer
from tortoise import Tortoise

from app.core.database import TORTOISE_ORM

commands = typer.Typer(help="Accident data commands.")


async def _with_db(coro: Awaitable[Any]) -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    try:
        await coro
    finally:
        await Tortoise.close_connections()


@commands.command()
def ingest(csv_path: str) -> None:
    """Load the aviation accident CSV (idempotent)."""
    from app.accidents.ingest import ingest as run_ingest

    asyncio.run(_with_db(run_ingest(csv_path)))
    typer.echo("Ingest done.")
