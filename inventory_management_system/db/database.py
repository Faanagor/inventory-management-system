import os

from dotenv import load_dotenv
from models import Base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Cargar variables de entorno
load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Crear el motor de base de datos asíncrono
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Crear las tablas en la base de datos (solo para pruebas, usa Alembic en producción)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Dependencia para obtener la sesión de base de datos
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
