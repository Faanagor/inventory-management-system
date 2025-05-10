"""Change Product and Inventory ID to UUID

Revision ID: 9d8652bf70e2
Revises: 2c74b7d66483
Create Date: 2025-02-23 06:20:38.833016

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# Identificadores de la migración
revision: str = "9d8652bf70e2"
down_revision: Union[str, None] = "2c74b7d66483"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convierte id de products e inventory de STRING/INTEGER a UUID correctamente."""

    # ✅ Convertir `id` de `products` de STRING a UUID
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=sa.VARCHAR(),
            type_=postgresql.UUID(),
            existing_nullable=False,
            postgresql_using="id::uuid",
        )

    # ✅ Convertir `id` de `inventory` de INTEGER a UUID (proceso manual)
    with op.batch_alter_table("inventory", schema=None) as batch_op:
        # Paso 1: Crear una nueva columna `id_uuid` de tipo UUID
        batch_op.add_column(sa.Column("id_uuid", postgresql.UUID(), nullable=True))

    # Paso 2: Llenar la nueva columna `id_uuid` con valores UUID aleatorios
    op.execute("UPDATE inventory SET id_uuid = gen_random_uuid()")

    with op.batch_alter_table("inventory", schema=None) as batch_op:
        # Paso 3: Eliminar la columna `id` antigua (INTEGER)
        batch_op.drop_column("id")

        # Paso 4: Renombrar `id_uuid` a `id` y establecer como PRIMARY KEY
        batch_op.alter_column("id_uuid", new_column_name="id", nullable=False)
        batch_op.create_primary_key("inventory_pkey", ["id"])

    # ✅ Convertir `product_id` y `store_id` en `inventory` a UUID
    with op.batch_alter_table("inventory", schema=None) as batch_op:
        batch_op.alter_column(
            "product_id",
            existing_type=sa.VARCHAR(),
            type_=postgresql.UUID(),
            existing_nullable=False,
            postgresql_using="product_id::uuid",
        )
        batch_op.alter_column(
            "store_id",
            existing_type=sa.VARCHAR(),
            type_=postgresql.UUID(),
            existing_nullable=False,
            postgresql_using="store_id::uuid",
        )


def downgrade() -> None:
    """Revierte la migración: convierte UUID de nuevo a STRING o INTEGER según el caso."""

    # 🔹 Revertir `id` de `products` de UUID a STRING
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.alter_column(
            "id",
            existing_type=postgresql.UUID(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
            postgresql_using="id::text",
        )

    # 🔹 Revertir `id` de `inventory` de UUID a INTEGER
    with op.batch_alter_table("inventory", schema=None) as batch_op:
        # Paso 1: Crear una nueva columna `id_integer` de tipo INTEGER con valores aleatorios
        batch_op.add_column(sa.Column("id_integer", sa.Integer(), nullable=True, autoincrement=True))

    # Paso 2: Asignar valores secuenciales a `id_integer`
    op.execute(
        """
        UPDATE inventory
        SET id_integer = nextval(pg_get_serial_sequence('inventory', 'id_integer'))
    """
    )

    with op.batch_alter_table("inventory", schema=None) as batch_op:
        # Paso 3: Eliminar `id` de tipo UUID
        batch_op.drop_column("id")

        # Paso 4: Renombrar `id_integer` a `id` y restaurar PRIMARY KEY
        batch_op.alter_column("id_integer", new_column_name="id", nullable=False)
        batch_op.create_primary_key("inventory_pkey", ["id"])

    # 🔹 Revertir `product_id` y `store_id` en `inventory` de UUID a STRING
    with op.batch_alter_table("inventory", schema=None) as batch_op:
        batch_op.alter_column(
            "product_id",
            existing_type=postgresql.UUID(),
            type_=sa.VARCHAR(),
            existing_nullable=False,
            postgresql_using="product_id::text",
        )
        batch_op.al
