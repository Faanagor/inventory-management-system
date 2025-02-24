from uuid import UUID

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inventory_management_system.models.inventory import Inventory
from inventory_management_system.schemas.inventory import InventoryCreate


async def get_inventory_by_store(store_id: UUID, db: AsyncSession):
    """Obtiene el inventario de una tienda específica."""
    query = select(Inventory).where(Inventory.store_id == store_id)
    result = await db.execute(query)
    return result.scalars().all()


async def create_inventory_entry(inventory_data: InventoryCreate, db: AsyncSession):
    """Crea una nueva entrada en el inventario."""
    new_inventory = Inventory(**inventory_data.model_dump())
    db.add(new_inventory)
    await db.commit()
    await db.refresh(new_inventory)
    return new_inventory


async def get_inventory_by_id(inventory_id: UUID, db: AsyncSession):
    """Obtiene un inventario por ID."""
    query = select(Inventory).where(Inventory.id == inventory_id)
    result = await db.execute(query)
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise NoResultFound(f"Inventario con ID {inventory_id} no encontrado")
    return inventory


async def update_inventory(inventory_id: UUID, quantity: int, db: AsyncSession):
    """Actualiza la cantidad de un inventario."""
    inventory = await get_inventory_by_id(inventory_id, db)
    inventory.quantity = quantity
    await db.commit()
    await db.refresh(inventory)
    return inventory


async def delete_inventory(inventory_id: UUID, db: AsyncSession):
    """Elimina un inventario."""
    inventory = await get_inventory_by_id(inventory_id, db)
    await db.delete(inventory)
    await db.commit()
    return {"message": "Inventario eliminado correctamente"}
