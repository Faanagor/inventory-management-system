from api.v1.routes import products
from db.database import Base, engine
from fastapi import FastAPI

# Crea las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(products.router, prefix="/api/v1")
