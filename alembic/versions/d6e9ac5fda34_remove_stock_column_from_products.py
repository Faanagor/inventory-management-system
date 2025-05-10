"""Remove stock column from products and adjust inventory constraints.

Revision ID: d6e9ac5fda34
Revises: 9d8652bf70e2
Create Date: 2025-02-24 07:32:20.707670

"""

import sqlalchemy as sa

from alembic import op

# Identificadores de la migración
revision = "d6e9ac5fda34"
down_revision = "9d8652bf70e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Elimina stock de products y ajusta claves foráneas en inventory."""
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.drop_column("stock")  # ✅ Eliminamos solo `stock`

    with op.batch_alter_table("inventory", schema=None) as batch_op:
        batch_op.alter_column("product_id", existing_type=sa.UUID(), nullable=False)
        batch_op.alter_column("store_id", existing_type=sa.UUID(), nullable=False)


def downgrade() -> None:
    """Reagrega la columna 'stock' en 'products' si se revierte la migración."""
    with op.batch_alter_table("products", schema=None) as batch_op:
        batch_op.add_column(sa.Column("stock", sa.INTEGER(), nullable=False, default=0))

    with op.batch_alter_table("inventory", schema=None) as batch_op:
        batch_op.alter_column("product_id", existing_type=sa.UUID(), nullable=True)
        batch_op.alter_column("store_id", existing_type=sa.UUID(), nullable=True)
