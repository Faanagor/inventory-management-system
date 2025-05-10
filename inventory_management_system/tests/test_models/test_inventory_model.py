import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.models import Inventory, Product


@pytest.fixture
async def sample_inventory(async_db_session: AsyncSession, sample_products):
    """Crea y devuelve un inventario de prueba vinculado a un producto existente."""
    product = sample_products[0]
    inventory = Inventory(
        product_id=product.id,
        store_id=uuid.uuid4(),
        quantity=100,
        min_stock=10,
    )
    async_db_session.add(inventory)
    await async_db_session.commit()
    await async_db_session.refresh(inventory)
    return inventory


@pytest.mark.asyncio
async def test_create_inventory(async_db_session: AsyncSession, sample_products):
    """Prueba la creación de un objeto Inventory en la base de datos."""
    product = sample_products[0]
    inventory = Inventory(
        product_id=product.id,
        store_id=uuid.uuid4(),
        quantity=50,
        min_stock=5,
    )
    async_db_session.add(inventory)
    await async_db_session.commit()
    await async_db_session.refresh(inventory)
    assert inventory.id is not None
    assert inventory.product_id == product.id
    assert inventory.quantity == 50
    assert inventory.min_stock == 5


@pytest.mark.asyncio
async def test_inventory_relationship_with_product(async_db_session: AsyncSession, sample_inventory):
    """Verifica que el inventario está correctamente vinculado a un producto."""
    inventory = sample_inventory
    product = await async_db_session.get(Product, inventory.product_id)
    assert product is not None
    assert product.id == inventory.product_id


@pytest.mark.asyncio
async def test_inventory_quantity_and_min_stock_cannot_be_negative(async_db_session: AsyncSession, sample_products):
    """Verifica que no se pueden asignar valores negativos a quantity o min_stock."""
    product = sample_products[0]
    inventory = Inventory(
        product_id=product.id,
        store_id=uuid.uuid4(),
        quantity=-10,  # Valor inválido
        min_stock=-5,  # Valor inválido
    )
    async_db_session.add(inventory)
    with pytest.raises(IntegrityError):
        await async_db_session.commit()
