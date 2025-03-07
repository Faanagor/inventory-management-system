from typing import List
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.db.database import get_db
from inventory_management_system.main import app
from inventory_management_system.models import Base, Inventory, Movement, Product
from inventory_management_system.schemas.movement import MovementType

DATABASE_URL = "sqlite+aiosqlite:///:memory:"  # Base de datos en memoria para pruebas
engine = create_async_engine(DATABASE_URL, echo=False, future=True)
# Crear sesión asíncrona
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Crea las tablas antes de cada prueba y las elimina después."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # Aquí se ejecutan las pruebas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def async_db_session():
    """Crea una sesión de base de datos asíncrona para pruebas."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")
async def override_get_db():
    """Sobrescribe la dependencia de la base de datos en FastAPI, asegurando una nueva sesión por solicitud."""

    async def _get_db():
        async with TestingSessionLocal() as session:
            yield session
            await session.rollback()
            await session.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db):
    """Cliente HTTP asíncrono para pruebas con FastAPI."""
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as client:
        yield client


@pytest.fixture
async def sample_products(async_db_session: AsyncSession) -> List[Product]:
    """Crea y devuelve una lista de productos de prueba."""
    products = [
        Product(
            name="Varilla Corrugada",
            description="Refuerzo estructural de concreto.",
            category="Construcción",
            price=25.50,
            sku="VARILLA123",
        ),
        Product(
            name="Alambrón",
            description="Alambre para refuerzo y estructuras.",
            category="Construcción",
            price=18.75,
            sku="ALAMBRO456",
        ),
        Product(
            name="Malla Electrosoldada",
            description="Red de alambres para construcción.",
            category="Construcción",
            price=35.20,
            sku="MALLA789",
        ),
    ]
    async_db_session.add_all(products)
    await async_db_session.flush()
    await async_db_session.commit()
    return products


@pytest.fixture
async def sample_inventory(async_db_session: AsyncSession, sample_products: List[Product]) -> List[Inventory]:
    """Crea tres inventarios de prueba en tiendas válidas."""
    store_ids = list(VALID_STORE_IDS)
    inventories = []
    for i in range(3):
        inventory = Inventory(
            product_id=sample_products[i % len(sample_products)].id,
            store_id=UUID(store_ids[i]),
            quantity=50 + (i * 10),
            min_stock=5,
        )
        async_db_session.add(inventory)
        inventories.append(inventory)
    await async_db_session.commit()
    for inventory in inventories:
        await async_db_session.refresh(inventory)
    return inventories


@pytest.fixture
async def sample_movements(async_db_session: AsyncSession, sample_inventory: List[Inventory]) -> List[Movement]:
    """Crea 4 movimientos de prueba usando productos del inventario."""
    product_1 = sample_inventory[0]
    product_2 = sample_inventory[1]
    store_1 = product_1.store_id
    store_2 = product_2.store_id
    movements = [
        Movement(
            product_id=product_1.id,
            source_store_id=store_1,
            target_store_id=store_2,
            quantity=10,
            type=MovementType.IN,
        ),
        Movement(
            product_id=product_2.id,
            source_store_id=store_2,
            target_store_id=store_1,
            quantity=5,
            type=MovementType.OUT,
        ),
        Movement(
            product_id=product_1.id,
            source_store_id=store_1,
            target_store_id=store_2,
            quantity=20,
            type=MovementType.TRANSFER,
        ),
        Movement(
            product_id=product_2.id,
            source_store_id=store_2,
            target_store_id=store_1,
            quantity=15,
            type=MovementType.IN,
        ),
    ]
    async_db_session.add_all(movements)
    await async_db_session.commit()
    return movements
