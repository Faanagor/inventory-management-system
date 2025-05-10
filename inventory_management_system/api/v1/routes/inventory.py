from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.db.database import get_db
from inventory_management_system.schemas.inventory import (
    InventoryCreate,
    InventoryResponse,
    InventoryTransferRequest,
    InventoryUpdate,
)
from inventory_management_system.services.inventory_service import (
    create_inventory,
    delete_inventory,
    get_inventory_by_id,
    get_inventory_by_store,
    get_low_stock_alerts,
    transfer_inventory,
    update_inventory,
)

router = APIRouter(tags=["Inventory"])


@router.post("/inventory/", response_model=InventoryResponse, status_code=201)
async def create_inventory_route(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva entrada en el inventario, validando que el producto exista."""
    return await create_inventory(inventory_data, db)


@router.get("/stores/{store_id}/inventory", response_model=list[InventoryResponse])
async def get_inventory_by_store_route(
    store_id: UUID, db: AsyncSession = Depends(get_db), limit: int = 100, offset: int = 0
):
    """Obtiene la lista de inventarios de una tienda con paginación."""
    return await get_inventory_by_store(store_id, db, limit, offset)


@router.post("/inventory/transfer", status_code=200)
async def transfer_inventory_route(transfer_data: InventoryTransferRequest, db: AsyncSession = Depends(get_db)):
    """Transfiere un producto entre tiendas, validando stock disponible."""
    return await transfer_inventory(transfer_data, db)


@router.get("/inventory/alerts")
async def get_low_stock_alerts_route(db: AsyncSession = Depends(get_db)):
    """Obtiene productos con stock bajo."""
    return await get_low_stock_alerts(db)


@router.get("/inventory/item/{inventory_id}", response_model=InventoryResponse)
async def get_inventory__by_id_route(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene un inventario por ID."""
    return await get_inventory_by_id(inventory_id, db)


@router.put("/inventory/{inventory_id}", response_model=InventoryResponse)
async def update_inventory_route(
    inventory_id: UUID, inventory_data: InventoryUpdate, db: AsyncSession = Depends(get_db)
):
    """Actualiza la cantidad o el stock mínimo de un inventario."""
    return await update_inventory(inventory_id, inventory_data, db)


@router.delete("/inventory/{inventory_id}")
async def delete_inventory_route(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Elimina un inventario, validando que exista."""
    return await delete_inventory(inventory_id, db)
