from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.db.database import get_db
from inventory_management_system.schemas.inventory import InventoryCreate, InventoryResponse, InventoryTransferRequest
from inventory_management_system.services.inventory_service import (
    create_inventory_entry,
    delete_inventory,
    get_inventory_by_id,
    get_inventory_by_store,
    get_low_stock_alerts,
    get_store_inventory,
    transfer_inventory,
    update_inventory,
)

router = APIRouter(tags=["Inventory"])


@router.post("/inventory/", response_model=InventoryResponse, status_code=201)
async def add_inventory(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva entrada en el inventario, validando que el producto exista."""
    return await create_inventory_entry(inventory_data, db)


@router.get("/stores/{store_id}/inventory", response_model=list[InventoryResponse])
async def get_store_inventory_route(store_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene el inventario de una tienda específica."""
    return await get_store_inventory(store_id, db)


@router.post("/inventory/transfer", status_code=200)
async def transfer_product(transfer_data: InventoryTransferRequest, db: AsyncSession = Depends(get_db)):
    """Transfiere un producto entre tiendas, validando stock disponible."""
    return await transfer_inventory(transfer_data, db)


@router.get("/inventory/alerts")
async def get_stock_alerts(db: AsyncSession = Depends(get_db)):
    """Obtiene productos con stock bajo."""
    return await get_low_stock_alerts(db)


@router.get("/inventory/{store_id}", response_model=list[InventoryResponse])
async def get_inventory(store_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene el inventario de una tienda."""
    return await get_inventory_by_store(store_id, db)


@router.get("/inventory/item/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene un inventario por ID."""
    try:
        return await get_inventory_by_id(inventory_id, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")


@router.put("/inventory/{inventory_id}", response_model=InventoryResponse)
async def update_inventory_quantity(inventory_id: UUID, quantity: int, db: AsyncSession = Depends(get_db)):
    """Actualiza la cantidad de un inventario."""
    try:
        return await update_inventory(inventory_id, quantity, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")


@router.delete("/inventory/{inventory_id}")
async def delete_inventory_item(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Elimina un inventario."""
    try:
        return await delete_inventory(inventory_id, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
