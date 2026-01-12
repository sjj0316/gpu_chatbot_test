"""fix collection owner id type and fk

Revision ID: 4b9f3a7d2c11
Revises: b7f2c9a1d8e4
Create Date: 2026-01-12 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b9f3a7d2c11"
down_revision: Union[str, Sequence[str], None] = "b7f2c9a1d8e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "collections",
        "owner_id",
        existing_type=sa.String(),
        type_=sa.Integer(),
        nullable=False,
        postgresql_using="owner_id::integer",
    )
    op.create_index(
        op.f("ix_collections_owner_id"),
        "collections",
        ["owner_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_collections_owner_id_users",
        "collections",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_collections_owner_id_users", "collections", type_="foreignkey"
    )
    op.drop_index(op.f("ix_collections_owner_id"), table_name="collections")
    op.alter_column(
        "collections",
        "owner_id",
        existing_type=sa.Integer(),
        type_=sa.String(),
        nullable=False,
        postgresql_using="owner_id::text",
    )
