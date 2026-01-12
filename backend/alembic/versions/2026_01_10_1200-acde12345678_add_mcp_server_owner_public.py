"""add mcp server owner and public flag

Revision ID: acde12345678
Revises: 17038bf1be51
Create Date: 2026-01-10 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "acde12345678"
down_revision: Union[str, Sequence[str], None] = "17038bf1be51"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mcp_servers",
        sa.Column("is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )
    op.add_column("mcp_servers", sa.Column("owner_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_mcp_servers_owner_id"), "mcp_servers", ["owner_id"], unique=False)
    op.create_foreign_key(
        "fk_mcp_servers_owner_id_users",
        "mcp_servers",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        """
        UPDATE mcp_servers
        SET owner_id = COALESCE(
            (SELECT id FROM users WHERE username = 'system' LIMIT 1),
            (SELECT id FROM users WHERE username = 'admin' LIMIT 1),
            (SELECT id FROM users ORDER BY id LIMIT 1)
        )
        WHERE owner_id IS NULL
        """
    )

    op.alter_column("mcp_servers", "owner_id", nullable=False)

    op.drop_constraint("mcp_servers_name_key", "mcp_servers", type_="unique")
    op.create_unique_constraint(
        "uq_mcp_servers_owner_name", "mcp_servers", ["owner_id", "name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_mcp_servers_owner_name", "mcp_servers", type_="unique")
    op.create_unique_constraint("mcp_servers_name_key", "mcp_servers", ["name"])

    op.drop_constraint("fk_mcp_servers_owner_id_users", "mcp_servers", type_="foreignkey")
    op.drop_index(op.f("ix_mcp_servers_owner_id"), table_name="mcp_servers")
    op.drop_column("mcp_servers", "owner_id")
    op.drop_column("mcp_servers", "is_public")
