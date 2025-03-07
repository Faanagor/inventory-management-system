import uuid
from typing import List

import pytest
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.models.inventory import Inventory
from inventory_management_system.schemas.inventory import InventoryCreate, InventoryTransferRequest, InventoryUpdate
from inventory_management_system.services.inventory_service import (
    create_inventory,
    delete_inventory,
    get_inventory_by_id,
    get_inventory_by_store,
    get_low_stock_alerts,
    transfer_inventory,
    update_inventory,
)


@pytest.mark.asyncio
async def test_create_inventory(async_db_session: AsyncSession, sample_products: List):
    """Prueba la creación de un nuevo inventario"""
    # 🔹 Generar UUIDs para producto y tienda
    product_id = sample_products[0].id
    store_id = list(VALID_STORE_IDS)[0]
    # 🔹 Datos de prueba corregidos
    inventory_data = InventoryCreate(
        product_id=product_id, store_id=store_id, quantity=10, min_stock=2  # Agregamos el campo requerido
    )
    # 🔹 Ejecutar la función
    new_inventory = await create_inventory(inventory_data, async_db_session)
    # 🔹 Verificar que se creó correctamente
    assert new_inventory is not None
    assert isinstance(new_inventory, Inventory)
    assert new_inventory.product_id == inventory_data.product_id
    assert new_inventory.store_id == inventory_data.store_id
    assert new_inventory.quantity == inventory_data.quantity
    assert new_inventory.min_stock == inventory_data.min_stock


@pytest.mark.asyncio
async def test_transfer_inventory(async_db_session: AsyncSession, sample_products):
    """Prueba la transferencia de inventario entre tiendas"""
    product_id = sample_products[0].id
    source_store_id = uuid.UUID(list(VALID_STORE_IDS)[0])
    target_store_id = uuid.UUID(list(VALID_STORE_IDS)[1])  # Una tienda diferente
    # 🔹 Crear inventario en la tienda de origen con stock suficiente
    source_inventory = Inventory(
        product_id=product_id,
        store_id=source_store_id,
        quantity=15,
        min_stock=3,
    )
    async_db_session.add(source_inventory)
    await async_db_session.commit()
    # 🔹 Datos de transferencia (mueve 5 unidades)
    transfer_data = InventoryTransferRequest(
        product_id=product_id, source_store_id=source_store_id, target_store_id=target_store_id, quantity=5
    )
    # 🔹 Ejecutar la transferencia
    response = await transfer_inventory(transfer_data, async_db_session)
    # 🔹 Verificar respuesta y actualización de stock
    assert response["message"] == "Transferencia completada con éxito"
    assert response["source_store"]["store_id"] == source_store_id
    assert response["source_store"]["remaining_stock"] == 10  # 15 - 5
    assert response["target_store"]["store_id"] == target_store_id
    assert response["target_store"]["new_stock"] == 5  # Nuevo inventario en tienda destino


@pytest.mark.asyncio
async def test_transfer_fails_due_to_low_stock(async_db_session: AsyncSession, sample_products):
    """Prueba que falle la transferencia si el stock en la tienda de origen queda por debajo del mínimo"""
    product_id = sample_products[0].id
    source_store_id = uuid.UUID(list(VALID_STORE_IDS)[0])
    target_store_id = uuid.UUID(list(VALID_STORE_IDS)[1])
    # 🔹 Crear inventario con poco stock
    source_inventory = Inventory(
        product_id=product_id,
        store_id=source_store_id,
        quantity=4,  # Solo 4 unidades disponibles
        min_stock=3,  # Mínimo permitido es 3
    )
    async_db_session.add(source_inventory)
    await async_db_session.commit()
    transfer_data = InventoryTransferRequest(
        product_id=product_id,
        source_store_id=source_store_id,
        target_store_id=target_store_id,
        quantity=3,  # Intentamos mover 3 unidades
    )
    # 🔹 Verificar que se lanza HTTPException 400
    with pytest.raises(HTTPException) as exc_info:
        await transfer_inventory(transfer_data, async_db_session)
    assert exc_info.value.status_code == 400
    assert "Producto a enviar sobrepasa el minimo stock" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_inventory_by_store(async_db_session: AsyncSession, sample_products):
    """Prueba obtener inventario de una tienda con paginación"""
    store_id = uuid.UUID(list(VALID_STORE_IDS)[0])
    inventory_item = Inventory(
        id=uuid.uuid4(),
        product_id=sample_products[0].id,
        store_id=store_id,
        quantity=10,
        min_stock=2,
    )
    async_db_session.add(inventory_item)
    await async_db_session.commit()
    result = await get_inventory_by_store(store_id, async_db_session, limit=1, offset=0)
    assert len(result) == 1
    assert result[0]["store_id"] == store_id


@pytest.mark.asyncio
async def test_get_low_stock_alerts(async_db_session: AsyncSession, sample_products):
    """Prueba obtener alertas de inventario bajo"""
    low_stock_item = Inventory(
        id=uuid.uuid4(),
        product_id=sample_products[0].id,
        store_id=uuid.UUID(list(VALID_STORE_IDS)[0]),
        quantity=1,
        min_stock=5,
    )
    async_db_session.add(low_stock_item)
    await async_db_session.commit()
    alerts = await get_low_stock_alerts(async_db_session)
    assert len(alerts) == 1
    assert alerts[0]["alert"] == "Stock bajo"


@pytest.mark.asyncio
async def test_get_inventory_by_id(async_db_session: AsyncSession, sample_products):
    """Prueba obtener inventario por ID"""
    inventory_id = uuid.uuid4()
    inventory_item = Inventory(
        id=inventory_id,
        product_id=sample_products[0].id,
        store_id=uuid.UUID(list(VALID_STORE_IDS)[0]),
        quantity=10,
        min_stock=2,
    )
    async_db_session.add(inventory_item)
    await async_db_session.commit()
    result = await get_inventory_by_id(inventory_id, async_db_session)
    assert result.id == inventory_id


@pytest.mark.asyncio
async def test_update_inventory(async_db_session: AsyncSession, sample_products):
    """Prueba actualizar el inventario"""
    inventory_id = uuid.uuid4()
    inventory_item = Inventory(
        id=inventory_id,
        product_id=sample_products[0].id,
        store_id=uuid.UUID(list(VALID_STORE_IDS)[0]),
        quantity=10,
        min_stock=2,
    )
    async_db_session.add(inventory_item)
    await async_db_session.commit()
    update_data = InventoryUpdate(quantity=15)
    updated_inventory = await update_inventory(inventory_id, update_data, async_db_session)
    assert updated_inventory.quantity == 15


@pytest.mark.asyncio
async def test_delete_inventory(async_db_session: AsyncSession, sample_products):
    """Prueba eliminar inventario"""
    inventory_id = uuid.uuid4()
    inventory_item = Inventory(
        id=inventory_id,
        product_id=sample_products[0].id,
        store_id=uuid.UUID(list(VALID_STORE_IDS)[0]),
        quantity=10,
        min_stock=2,
    )
    async_db_session.add(inventory_item)
    await async_db_session.commit()
    response = await delete_inventory(inventory_id, async_db_session)
    assert response["message"] == "Inventario eliminado correctamente"
    with pytest.raises(HTTPException) as exc:
        await get_inventory_by_id(inventory_id, async_db_session)
    assert exc.value.status_code == 404
