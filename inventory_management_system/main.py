import uvicorn
from api.v1.routes import products
from db.database import Base, engine
from db.migrations import apply_migrations
from fastapi import FastAPI

# Crea las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory Management System", version="1.0.0")

app.include_router(products.router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """Ejecutar migraciones al iniciar FastAPI"""
    await apply_migrations()


@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Management System API!"}


if __name__ == "__main__":
    uvicorn.run("inventory_management_system.main:app", host="127.0.0.1", port=8000, reload=True)
