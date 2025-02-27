import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
from inventory_management_system.db.database import SQLALCHEMY_DATABASE_URL
from inventory_management_system.models import Base
from inventory_management_system.models.inventory import Inventory
from inventory_management_system.models.movement import Movement
from inventory_management_system.models.product import Product

# Configuración de logging de Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Agrega los modelos para generar las migraciones
target_metadata = Base.metadata


# Configura el engine asíncrono
def get_engine():
    return async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        future=True,
    )


async def run_migrations():
    """Ejecuta las migraciones de Alembic de manera asíncrona."""
    connectable = get_engine()
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    """Aplica las migraciones usando una conexión dada."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        transaction_per_migration=True,
        render_as_batch=True,  # Necesario para SQLite
        compare_type=True,  # 🔹 Compara tipos para evitar eliminaciones accidentales
    )
    with context.begin_transaction():
        context.run_migrations()


# Ejecuta el código dependiendo de si está en modo offline o online
if context.is_offline_mode():
    context.configure(
        url=SQLALCHEMY_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,  # 🔹 Asegura que no se eliminen tablas inesperadamente
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    asyncio.run(run_migrations())  # 🔹 Usa `asyncio.run()` para llamar `run_migrations()`
