import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from inventory_management_system.db.database import get_db
from inventory_management_system.main import app
from inventory_management_system.models import Base
from inventory_management_system.schemas.product import ProductCreate

# Configuración de Base de Datos en Memoria para pruebas
DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Dependency override para usar la BD de pruebas
async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# Datos de prueba compartidos
@pytest.fixture
def product_data():
    """Fixture que proporciona datos de prueba para productos."""
    return {
        "name": "Producto de Prueba",
        "description": "Descripción de prueba",
        "category": "Electrónica",
        "price": 99.99,
        "sku": "TEST1234",
        "stock": 50,
    }


@pytest.fixture
def product_create(product_data):
    """Fixture que devuelve una instancia de ProductCreate basada en product_data."""
    return ProductCreate(**product_data)


@pytest.fixture
def product_update_data():
    """Fixture que proporciona datos diferentes para actualizar un producto."""
    return {
        "name": "Producto Actualizado",
        "description": "Nueva descripción",
        "category": "Hogar",
        "price": 79.99,
        "sku": "UPDATED1234",
        "stock": 30,
    }


@pytest.fixture
def product_update(product_update_data):
    """Fixture que devuelve una instancia de ProductCreate basada en product_data."""
    return ProductCreate(**product_update_data)


@pytest.fixture(scope="module")
async def async_client():
    """Cliente HTTP asíncrono para pruebas"""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
async def async_session():
    """Crea una sesión de base de datos asíncrona para pruebas."""
    async with TestingSessionLocal() as session:
        yield session  # Retorna la sesión para ser usada en las pruebas
        await session.rollback()  # Revierte los cambios después de cada prueba


@pytest.fixture(scope="module", autouse=True)
async def setup_db():
    """Crea la base de datos en memoria antes de las pruebas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function", autouse=True)
async def clean_db():
    """Limpia la base de datos antes de cada prueba."""
    async with TestingSessionLocal() as session:
        await session.execute(text("DELETE FROM products"))
        await session.commit()
