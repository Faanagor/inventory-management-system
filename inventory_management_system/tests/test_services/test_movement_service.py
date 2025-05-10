import uuid
from datetime import UTC, datetime
from typing import List

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.models import Inventory
from inventory_management_system.models.movement import Movement, MovementType
from inventory_management_system.schemas.movement import MovementCreate
from inventory_management_system.services.movement_service import create_movement, get_all_movements, get_movement_by_id


@pytest.mark.asyncio
async def test_create_movement(async_db_session: AsyncSession, sample_inventory: List[Inventory]):
    """Prueba la creación de un nuevo movimiento en el inventario"""
    # Seleccionar un inventario existente
    inventory_item = sample_inventory[0]
    movement_data = MovementCreate(
        product_id=inventory_item.product_id,
        source_store_id=inventory_item.store_id,
        target_store_id=uuid.UUID(list(VALID_STORE_IDS)[1]),
        quantity=5,
        type=MovementType.TRANSFER,
        timestamp=datetime.now(UTC),
    )
    response = await create_movement(movement_data, async_db_session)
    # Verifica que se creó un movimiento y tiene los datos esperados
    assert response is not None
    assert isinstance(response, Movement)
    assert response.product_id == movement_data.product_id
    assert response.source_store_id == movement_data.source_store_id
    assert response.target_store_id == movement_data.target_store_id
    assert response.quantity == movement_data.quantity
    assert response.type == movement_data.type


@pytest.mark.asyncio
async def test_get_all_movements(async_db_session: AsyncSession, sample_movements: List[Movement]):
    """Prueba la obtención de todos los movimientos registrados en la base de datos."""
    # Llamamos a la función de servicio
    movements = await get_all_movements(async_db_session)
    # Verificamos que la cantidad de movimientos obtenidos es al menos la cantidad en sample_movements
    assert len(movements) >= len(sample_movements)
    # Verificamos que los movimientos sean del tipo correcto
    assert all(isinstance(movement, Movement) for movement in movements)


@pytest.mark.asyncio
async def test_get_movement_by_id(async_db_session: AsyncSession, sample_movements: List[Movement]):
    """Prueba la obtención de un movimiento por su ID usando datos de sample_movements"""
    # Tomamos un movimiento existente de sample_movements
    movement = sample_movements[0]
    # Llamamos al servicio para obtener el movimiento por ID
    fetched_movement = await get_movement_by_id(async_db_session, movement.id)
    # Verificamos que el movimiento se haya encontrado y tenga los datos correctos
    assert fetched_movement is not None
    assert fetched_movement.id == movement.id
    assert fetched_movement.quantity == movement.quantity
    assert fetched_movement.type == movement.type


@pytest.mark.asyncio
async def test_get_movement_by_id_not_found(async_db_session: AsyncSession):
    """Prueba que se levante una excepción al buscar un ID inexistente"""
    fake_id = uuid.uuid4()
    with pytest.raises(HTTPException) as exc_info:
        await get_movement_by_id(async_db_session, fake_id)
    assert exc_info.value.status_code == 404
    assert f"No se encontró un movimiento con ID {fake_id}" in exc_info.value.detail
