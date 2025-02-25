from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func

from inventory_management_system.config import VALID_STORE_IDS
from inventory_management_system.models.inventory import Inventory
from inventory_management_system.models.product import Product
from inventory_management_system.schemas.inventory import InventoryCreate, InventoryTransferRequest, InventoryUpdate


async def _get_product_by_id(product_id: UUID, db: AsyncSession) -> Product:
    """Valida si el producto existe en la base de datos."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="El producto no está registrado en la base de datos.")
    return product


async def _validate_store_id(store_id: UUID):
    """Verifica si una tienda es válida antes de continuar con la operación."""
    if str(store_id) not in VALID_STORE_IDS:
        raise HTTPException(status_code=400, detail="Tienda no válida.")


async def _check_inventory_exists(product_id: UUID, store_id: UUID, db: AsyncSession) -> bool:
    """Verifica si un producto ya está registrado en el inventario de una tienda específica."""
    await _validate_store_id(store_id)
    result = await db.execute(
        select(Inventory).where((Inventory.product_id == product_id) & (Inventory.store_id == store_id))
    )
    return result.scalar_one_or_none() is not None


async def _get_inventory_record(product_id: UUID, store_id: UUID, db: AsyncSession) -> Inventory | None:
    """Obtiene un registro de inventario específico para un producto en una tienda."""
    await _validate_store_id(store_id)
    result = await db.execute(
        select(Inventory).where((Inventory.product_id == product_id) & (Inventory.store_id == store_id))
    )
    return result.scalar_one_or_none()


async def create_inventory(inventory_data: InventoryCreate, db: AsyncSession) -> Inventory:
    """
    Crea una nueva entrada en el inventario, validando que el producto exista
    y que no esté duplicado en la misma tienda.
    """
    # 🔹 Validar que el producto existe
    await _get_product_by_id(inventory_data.product_id, db)
    # 🔹 Validar que el producto no esté duplicado en la tienda
    if await _check_inventory_exists(inventory_data.product_id, inventory_data.store_id, db):
        raise HTTPException(
            status_code=409, detail="El producto ya está registrado en esta tienda. Usa la opción de actualizar stock."
        )
    # 🔹 Crear nueva entrada en `inventory`
    new_inventory = Inventory(**inventory_data.model_dump())
    db.add(new_inventory)
    await db.commit()
    await db.refresh(new_inventory)
    return new_inventory


async def get_inventory_by_store(store_id: UUID, db: AsyncSession, limit: int | None = 100, offset: int = 0):
    """Obtiene el inventario de una tienda con opción de paginación."""
    await _validate_store_id(store_id)
    query = select(
        Inventory.id,
        Inventory.product_id,
        Inventory.store_id,
        Inventory.quantity,
        func.coalesce(Inventory.min_stock, 0).label("min_stock"),
    ).where(Inventory.store_id == store_id)
    if limit:  # Si limit es None, no aplicar paginación
        query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.mappings().all()  # Retorna diccionarios en lugar de objetos SQLAlchemy


async def transfer_inventory(transfer_data: InventoryTransferRequest, db: AsyncSession):
    """Transfiere stock de un producto de una tienda a otra, validando stock disponible."""
    # 🔹 Obtener el inventario de la tienda de origen
    source_product = await _get_product_by_id(transfer_data.product_id, db)
    if not source_product:
        raise HTTPException(status_code=404, detail="El producto no existe en la base de datos.")
    source_inventory = await _get_inventory_record(transfer_data.product_id, transfer_data.source_store_id, db)
    if not source_inventory:
        raise HTTPException(status_code=404, detail="El producto no existe en la tienda de origen.")
    if source_inventory.quantity < transfer_data.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Stock insuficiente en la tienda de origen. Stock actual: {source_inventory.quantity}",
        )
    # 🔹 Obtener o crear el inventario en la tienda de destino
    target_inventory = await _get_inventory_record(transfer_data.product_id, transfer_data.target_store_id, db)
    if not target_inventory:
        target_inventory = Inventory(
            product_id=transfer_data.product_id,
            store_id=transfer_data.target_store_id,
            quantity=0,
            min_stock=5,  # 🔹 Se puede configurar desde un parámetro global si es necesario
        )
        db.add(target_inventory)
    # 🔹 Realizar la transferencia
    source_inventory.quantity -= transfer_data.quantity
    target_inventory.quantity += transfer_data.quantity
    await db.commit()
    await db.refresh(source_inventory)
    await db.refresh(target_inventory)
    return {
        "message": "Transferencia completada con éxito",
        "source_store": {"store_id": transfer_data.source_store_id, "remaining_stock": source_inventory.quantity},
        "target_store": {"store_id": transfer_data.target_store_id, "new_stock": target_inventory.quantity},
    }


async def get_low_stock_alerts(db: AsyncSession):
    """Lista productos con stock bajo en cualquier tienda."""
    query = select(Inventory).where(Inventory.quantity <= Inventory.min_stock)
    result = await db.execute(query)
    low_stock_items = result.scalars().all()

    return [
        {
            "product_id": item.product_id,
            "store_id": item.store_id,
            "quantity": item.quantity,
            "min_stock": item.min_stock,
            "alert": "Stock crítico" if item.quantity == 0 else "Stock bajo",
        }
        for item in low_stock_items
    ]


async def get_inventory_by_id(inventory_id: UUID, db: AsyncSession) -> Inventory:
    """Obtiene un inventario por ID o lanza una excepción si no existe."""
    result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventario no encontrado.")
    return inventory


async def update_inventory(inventory_id: UUID, inventory_data: InventoryUpdate, db: AsyncSession) -> Inventory:
    """Actualiza la cantidad o el stock mínimo de un inventario existente sin sobrescribir valores no
    proporcionados."""
    inventory = await get_inventory_by_id(inventory_id, db)
    # Validación en services porque en update puede venir solo quantity o min_stock
    update_data = inventory_data.model_dump(exclude_unset=True)
    new_quantity = update_data.get("quantity", inventory.quantity)
    new_min_stock = update_data.get("min_stock", inventory.min_stock)
    if new_quantity < new_min_stock:
        raise HTTPException(status_code=400, detail="La cantidad no puede ser menor al stock mínimo.")
    for key, value in update_data.items():
        setattr(inventory, key, value)
    await db.commit()
    await db.refresh(inventory)
    return inventory


async def delete_inventory(inventory_id: UUID, db: AsyncSession):
    """Elimina un inventario, validando que exista."""
    inventory = await get_inventory_by_id(inventory_id, db)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    await db.delete(inventory)
    await db.commit()
    return {"message": "Inventario eliminado correctamente"}
