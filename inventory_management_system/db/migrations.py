import logging
import subprocess


def apply_migrations():
    """Ejecuta las migraciones de Alembic de manera sincrónica."""
    try:
        logging.info("⏳ Ejecutando migraciones con Alembic...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logging.info("✅ Migraciones aplicadas correctamente.")
    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Error al ejecutar las migraciones: {e}")
