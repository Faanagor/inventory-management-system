from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inventory_management_system.models.movement import Movement, MovementType
from inventory_management_system.schemas.movement import MovementCreate


async def create_movement(movement_data: MovementCreate, db: AsyncSession) -> Movement | None:
    """Servicio principal para manejar la creación de movimientos de inventario."""
    movement_data = movement_data.model_copy()
    movement_data.timestamp = (
        movement_data.timestamp.replace(tzinfo=None) if movement_data.timestamp else datetime.now().replace(tzinfo=None)
    )
    movement_data.type = movement_data.type or MovementType.OUT
    new_movement = Movement(**movement_data.model_dump(exclude_unset=True))
    db.add(new_movement)
    await db.commit()
    await db.refresh(new_movement)
    return new_movement


async def get_all_movements(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    product_id: Optional[UUID] = None,
    movement_type: Optional[MovementType] = None,
    date: Optional[datetime] = None,
    store_id: Optional[UUID] = None,
) -> Movement | None:
    """Obtiene todos los movimientos con paginación y filtros."""
    stmt = select(Movement).order_by(Movement.timestamp.desc()).offset(skip).limit(limit)
    # Aplicar filtros opcionales
    if product_id:
        stmt = stmt.where(Movement.product_id == product_id)
    if movement_type:
        stmt = stmt.where(Movement.type == movement_type)
    if date:
        stmt = stmt.where(Movement.timestamp >= datetime.combine(date, datetime.min.time()))
    if store_id:
        stmt = stmt.where((Movement.source_store_id == store_id) | (Movement.target_store_id == store_id))
    result = await db.execute(stmt)
    movements = result.scalars().all()
    if not movements:
        raise HTTPException(status_code=404, detail="No hay movimientos registrados.")
    return movements


async def get_movement_by_id(db: AsyncSession, movement_id: UUID) -> Movement | None:
    """Obtiene un movimiento específico por su ID."""
    stmt = select(Movement).where(Movement.id == movement_id)
    result = await db.execute(stmt)
    movement = result.scalars().first()
    if not movement:
        raise HTTPException(status_code=404, detail=f"No se encontró un movimiento con ID {movement_id}")
    return movement
