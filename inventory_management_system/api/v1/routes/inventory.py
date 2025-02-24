from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.db.database import get_db
from inventory_management_system.schemas.inventory import InventoryCreate, InventoryResponse
from inventory_management_system.services.inventory_service import (
    create_inventory_entry,
    delete_inventory,
    get_inventory_by_id,
    get_inventory_by_store,
    update_inventory,
)

router = APIRouter(tags=["Inventory"])


@router.get("/{store_id}", response_model=list[InventoryResponse])
async def get_inventory(store_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene el inventario de una tienda."""
    return await get_inventory_by_store(store_id, db)


@router.post("/", response_model=InventoryResponse)
async def add_inventory(inventory_data: InventoryCreate, db: AsyncSession = Depends(get_db)):
    """Crea una nueva entrada en el inventario."""
    return await create_inventory_entry(inventory_data, db)


@router.get("/item/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Obtiene un inventario por ID."""
    try:
        return await get_inventory_by_id(inventory_id, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory_quantity(inventory_id: UUID, quantity: int, db: AsyncSession = Depends(get_db)):
    """Actualiza la cantidad de un inventario."""
    try:
        return await update_inventory(inventory_id, quantity, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")


@router.delete("/{inventory_id}")
async def delete_inventory_item(inventory_id: UUID, db: AsyncSession = Depends(get_db)):
    """Elimina un inventario."""
    try:
        return await delete_inventory(inventory_id, db)
    except Exception:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
