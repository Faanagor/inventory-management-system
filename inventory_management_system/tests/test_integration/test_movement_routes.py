from datetime import datetime, timezone
from typing import List

import pytest
from httpx import AsyncClient

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.models import Inventory
from inventory_management_system.models.movement import Movement, MovementType


@pytest.mark.asyncio
async def test_create_movement(async_client: AsyncClient, sample_inventory: List[Inventory]):
    """Prueba la creación de un movimiento de inventario."""
    movement_data = {
        "product_id": str(sample_inventory[0].id),
        "source_store_id": str(sample_inventory[0].store_id),
        "target_store_id": str(list(VALID_STORE_IDS)[1]),
        "quantity": 15,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": MovementType.TRANSFER,
    }
    response = await async_client.post("/api/movements/", json=movement_data)
    assert response.status_code == 201
    response_data = response.json()
    assert response_data["product_id"] == movement_data["product_id"]
    assert response_data["source_store_id"] == movement_data["source_store_id"]
    assert response_data["target_store_id"] == movement_data["target_store_id"]
    assert response_data["quantity"] == movement_data["quantity"]
    assert response_data["type"] == movement_data["type"]


@pytest.mark.asyncio
async def test_get_all_movements(async_client: AsyncClient, sample_movements: List[Movement]):
    """Prueba la obtención de todos los movimientos sin filtros ni paginación."""
    response = await async_client.get("/api/movements/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 4  # Debe devolver todos los movimientos creados


@pytest.mark.asyncio
async def test_get_all_movements_pagination(async_client: AsyncClient, sample_movements: List[Movement]):
    """Prueba la paginación de movimientos con un límite de 3 registros."""
    response = await async_client.get("/api/movements/", params={"limit": 3})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 3  # Verifica que solo se devuelven 3 movimientos


@pytest.mark.asyncio
async def test_get_movement_by_id(async_client: AsyncClient, sample_movements: List[Movement]):
    """Prueba la obtención de un movimiento por su ID."""
    movement = sample_movements[0]  # Tomamos el primer movimiento de la lista
    response = await async_client.get(f"/api/movements/{movement.id}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["id"] == str(movement.id)  # Convertimos el UUID a string para comparar correctamente
