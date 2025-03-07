from typing import List

import pytest
from httpx import AsyncClient

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.models import Inventory, Product


@pytest.mark.asyncio
async def test_create_inventory(async_client: AsyncClient, sample_products: List[Product]):
    """Prueba la creación de un nuevo inventario."""
    new_inventory = {
        "store_id": str(list(VALID_STORE_IDS)[0]),
        "product_id": str(sample_products[0].id),
        "quantity": 100,
        "min_stock": 10,
    }
    response = await async_client.post("/api/inventory/", json=new_inventory)
    assert response.status_code == 201
    assert response.json()["store_id"] == new_inventory["store_id"]
    assert response.json()["product_id"] == new_inventory["product_id"]
    assert response.json()["quantity"] == new_inventory["quantity"]
    assert response.json()["min_stock"] == new_inventory["min_stock"]


@pytest.mark.asyncio
async def test_get_inventory_by_store(async_client: AsyncClient):
    """Prueba obtener el inventario de una tienda."""
    valid_store_id = str(list(VALID_STORE_IDS)[0])
    response = await async_client.get(f"/api/stores/{valid_store_id}/inventory")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_transfer_inventory(async_client: AsyncClient, sample_inventory: List[Inventory]):
    """Prueba la transferencia de inventario entre tiendas usando los inventarios de prueba."""
    transfer_data = {
        "product_id": str(sample_inventory[0].product_id),
        "source_store_id": str(sample_inventory[0].store_id),
        "target_store_id": str(list(VALID_STORE_IDS)[1]),
        "quantity": 10,
    }
    response = await async_client.post("/api/inventory/transfer", json=transfer_data)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_low_stock_alerts(async_client: AsyncClient):
    """Prueba obtener alertas de stock bajo."""
    response = await async_client.get("/api/inventory/alerts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_inventory_by_id(async_client: AsyncClient, sample_inventory: List[Inventory]):
    """Prueba obtener un inventario por su ID."""
    inventory_id = str(sample_inventory[0].id)
    response = await async_client.get(f"/api/inventory/item/{inventory_id}")
    assert response.status_code == 200
    assert response.json()["id"] == inventory_id


@pytest.mark.asyncio
async def test_update_inventory(async_client: AsyncClient, sample_inventory: List[Inventory]):
    """Prueba actualizar un inventario."""
    inventory_id = str(sample_inventory[0].id)
    update_data = {"quantity": 150}
    response = await async_client.put(f"/api/inventory/{inventory_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["quantity"] == update_data["quantity"]


@pytest.mark.asyncio
async def test_delete_inventory(async_client: AsyncClient, sample_inventory: List[Inventory]):
    """Prueba eliminar un inventario."""
    inventory_id = str(sample_inventory[0].id)
    response = await async_client.delete(f"/api/inventory/{inventory_id}")
    assert response.status_code == 200

    # Verificar que el inventario ya no existe
    response = await async_client.get(f"/inventory/item/{inventory_id}")
    assert response.status_code == 404
