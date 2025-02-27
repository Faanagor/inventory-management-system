from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from inventory_management_system.models.movement import Movement, MovementType
from inventory_management_system.schemas.movement import MovementCreate


async def create_movement(movement_data: MovementCreate, db: AsyncSession):
    """Servicio principal para manejar la creación de movimientos de inventario."""
    movement_data.timestamp = movement_data.timestamp.replace(tzinfo=None)
    if movement_data.type is None:
        movement_data.type = MovementType.OUT
    new_movement = Movement(**movement_data.model_dump())
    db.add(new_movement)
    await db.commit()
    await db.refresh(new_movement)
    return {"message": "Movimiento de entrada registrado exitosamente."}


async def get_all_movements(db: AsyncSession):
    """Obtiene todos los movimientos registrados en la base de datos."""
    stmt = select(Movement).order_by(Movement.timestamp.desc())
    result = await db.execute(stmt)
    movements = result.scalars().all()
    if not movements:
        raise HTTPException(status_code=404, detail="No hay movimientos registrados.")
    return movements


async def get_movement_by_id(movement_id: UUID, db: AsyncSession):
    """Obtiene un movimiento específico por su ID."""
    stmt = select(Movement).where(Movement.id == movement_id)
    result = await db.execute(stmt)
    movement = result.scalars().first()
    if not movement:
        raise HTTPException(status_code=404, detail=f"No se encontró un movimiento con ID {movement_id}")
    return movement
