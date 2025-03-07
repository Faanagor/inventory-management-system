import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from inventory_management_system.models import Base

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de base de datos asíncrono
engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Crear las tablas en la base de datos (solo para pruebas, usa Alembic en producción)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependencia para obtener la sesión de base de datos
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
