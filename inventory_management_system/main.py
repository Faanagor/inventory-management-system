import asyncio
import logging
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI

from inventory_management_system.api.v1.routes import products
from inventory_management_system.db.migrations import apply_migrations

app = FastAPI(title="Inventory Management System", version="1.0.0")
app.include_router(products.router, prefix="/api")


async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manejador de ciclo de vida para aplicar migraciones al iniciar la API."""
    logging.info("⏳ Aplicando migraciones de Alembic...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, apply_migrations)
    logging.info("✅ Migraciones aplicadas correctamente.")
    yield  # Aquí se ejecuta la aplicación
    logging.info("🛑 Cerrando la aplicación...")


@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Management System API!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
