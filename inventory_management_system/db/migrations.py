import asyncio

from db.database import engine

from alembic import command, config


async def apply_migrations():
    """Aplica migraciones de Alembic de manera automática."""
    alembic_cfg = config.Config("alembic.ini")
    async with engine.begin() as conn:
        await conn.run_sync(command.upgrade, alembic_cfg, "head")


if __name__ == "__main__":
    asyncio.run(apply_migrations())
