from datetime import date
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from inventory_management_system.db.database import get_db
from inventory_management_system.models.movement import MovementType
from inventory_management_system.schemas.movement import MovementCreate, MovementResponse
from inventory_management_system.services.movement_service import create_movement, get_all_movements, get_movement_by_id

router = APIRouter(tags=["Movements"])


@router.post("/", response_model=MovementResponse, status_code=201)
async def create_movement_route(movement_data: MovementCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo movimiento de inventario.
    """
    return await create_movement(db, movement_data)


@router.get("/", response_model=List[MovementResponse])
async def get_all_movements_route(
    db: AsyncSession = Depends(get_db),
    skip: int = Query(0, alias="offset", ge=0, description="Número de movimientos a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de movimientos a devolver"),
    product_id: Optional[UUID] = Query(None, description="Filtrar por ID del producto"),
    movement_type: Optional[MovementType] = Query(
        None, description="Filtrar por tipo de movimiento (IN, OUT, TRANSFER)"
    ),
    date: Optional[date] = Query(None, description="Filtrar por fecha del movimiento"),
    store_id: Optional[UUID] = Query(None, description="Filtrar por ID de la tienda"),
):
    """
    Obtiene todos los movimientos de inventario con paginación y filtros.
    """
    return await get_all_movements(
        db, skip=skip, limit=limit, product_id=product_id, movement_type=movement_type, date=date, store_id=store_id
    )


@router.get("/{movement_id}", response_model=MovementResponse)
async def get_movement_by_id_route(movement_id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtiene un movimiento de inventario por su ID.
    """
    return await get_movement_by_id(db, movement_id)
