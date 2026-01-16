"""fix system user email

Revision ID: 8f1e9b4d2c3a
Revises: 4b9f3a7d2c11
Create Date: 2026-01-15 03:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f1e9b4d2c3a"
down_revision: Union[str, Sequence[str], None] = "4b9f3a7d2c11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE users
            SET email = 'system@example.com'
            WHERE username = 'system'
              AND (email IS NULL OR email NOT LIKE '%@%.%')
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            UPDATE users
            SET email = 'system@local'
            WHERE username = 'system'
            """
        )
    )
