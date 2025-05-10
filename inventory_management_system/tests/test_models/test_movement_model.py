import uuid

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.models.movement import Movement, MovementType
from inventory_management_system.models.product import Product


@pytest.fixture
async def sample_movement(async_db_session: AsyncSession, sample_products):
    """Crea y devuelve un movimiento de prueba vinculado a un producto existente."""
    product = sample_products[0]
    movement = Movement(
        product_id=product.id,
        source_store_id=uuid.uuid4(),
        target_store_id=uuid.uuid4(),
        quantity=20,
        type=MovementType.IN,
    )
    async_db_session.add(movement)
    await async_db_session.commit()
    await async_db_session.refresh(movement)
    return movement


@pytest.fixture
async def create_movement(async_db_session: AsyncSession, sample_products):
    """Fixture para crear movimientos dinámicamente."""

    async def _create_movement(quantity=10, type=MovementType.IN):
        product = sample_products[0]
        movement = Movement(
            product_id=product.id,
            source_store_id=uuid.uuid4(),
            target_store_id=uuid.uuid4(),
            quantity=quantity,
            type=type,
        )
        async_db_session.add(movement)
        await async_db_session.commit()
        await async_db_session.refresh(movement)
        return movement

    return _create_movement


@pytest.mark.asyncio
async def test_create_movement(create_movement):
    """Prueba la creación de un objeto Movement en la base de datos."""
    movement = await create_movement(quantity=15, type=MovementType.OUT)
    assert movement.id is not None
    assert movement.quantity == 15
    assert movement.type == MovementType.OUT


@pytest.mark.asyncio
async def test_movement_relationship_with_product(async_db_session: AsyncSession, sample_movement):
    """Verifica que el movimiento está correctamente vinculado a un producto."""
    movement = sample_movement
    product = await async_db_session.get(Product, movement.product_id)
    assert product is not None
    assert product.id == movement.product_id


@pytest.mark.asyncio
async def test_movement_quantity_cannot_be_negative(async_db_session: AsyncSession, sample_products):
    """Verifica que no se puede asignar un valor negativo a quantity."""
    product = sample_products[0]
    movement = Movement(
        product_id=product.id,
        source_store_id=uuid.uuid4(),
        target_store_id=uuid.uuid4(),
        quantity=-10,
        type=MovementType.TRANSFER,
    )
    async_db_session.add(movement)
    with pytest.raises(IntegrityError):
        await async_db_session.commit()
    await async_db_session.rollback()


@pytest.mark.asyncio
async def test_movement_type_is_valid(sample_products):
    """Verifica que el campo type solo acepte valores válidos de MovementType."""
    product = sample_products[0]
    with pytest.raises(ValueError, match="Invalid movement type"):
        Movement(
            product_id=product.id,
            source_store_id=uuid.uuid4(),
            target_store_id=uuid.uuid4(),
            quantity=10,
            type="INVALID_TYPE",
        )
