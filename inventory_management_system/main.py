import asyncio
import logging

import uvicorn
from api.v1.routes import products
from db.migrations import apply_migrations
from fastapi import FastAPI

app = FastAPI(title="Inventory Management System", version="1.0.0")
app.include_router(products.router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Aplica migraciones al iniciar la API."""
    logging.info("⏳ Aplicando migraciones de Alembic...")
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, apply_migrations)
    logging.info("✅ Migraciones aplicadas correctamente.")


@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Management System API!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
