"""add llm api keys

Revision ID: b7f2c9a1d8e4
Revises: 6c2a0c7e9e2a
Create Date: 2026-01-12 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "b7f2c9a1d8e4"
down_revision: Union[str, Sequence[str], None] = "6c2a0c7e9e2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    llm_provider = postgresql.ENUM(
        "openai",
        "anthropic",
        "google",
        "mistral",
        "azure_openai",
        "groq",
        "local",
        "other",
        name="llm_provider",
        create_type=False,
    )
    llm_purpose = postgresql.ENUM(
        "chat",
        "embedding",
        name="llm_purpose",
        create_type=False,
    )
    bind = op.get_bind()
    llm_provider.create(bind, checkfirst=True)
    llm_purpose.create(bind, checkfirst=True)

    op.create_table(
        "llm_api_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alias", sa.String(length=50), nullable=True),
        sa.Column("provider", llm_provider, nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("endpoint_url", sa.String(length=255), nullable=True),
        sa.Column("purpose", llm_purpose, nullable=False),
        sa.Column("api_key", sa.Text(), nullable=False),
        sa.Column(
            "is_public", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("extra", sa.JSON(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "alias", name="uq_llmkey_owner_alias"),
        sa.UniqueConstraint(
            "owner_id",
            "provider",
            "model",
            "endpoint_url",
            name="uq_llmkey_owner_provider_model_endpoint",
        ),
    )
    op.create_index(op.f("ix_llm_api_keys_id"), "llm_api_keys", ["id"], unique=False)
    op.create_index(
        op.f("ix_llm_api_keys_is_active"),
        "llm_api_keys",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        op.f("ix_llm_api_keys_is_public"),
        "llm_api_keys",
        ["is_public"],
        unique=False,
    )
    op.create_index(
        "ix_llmkey_public_active",
        "llm_api_keys",
        ["is_public", "is_active"],
        unique=False,
    )
    op.create_index(
        "ix_llmkey_provider_purpose",
        "llm_api_keys",
        ["provider", "purpose"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_llmkey_provider_purpose", table_name="llm_api_keys")
    op.drop_index("ix_llmkey_public_active", table_name="llm_api_keys")
    op.drop_index(op.f("ix_llm_api_keys_is_public"), table_name="llm_api_keys")
    op.drop_index(op.f("ix_llm_api_keys_is_active"), table_name="llm_api_keys")
    op.drop_index(op.f("ix_llm_api_keys_id"), table_name="llm_api_keys")
    op.drop_table("llm_api_keys")

    bind = op.get_bind()
    postgresql.ENUM(name="llm_purpose").drop(bind, checkfirst=True)
    postgresql.ENUM(name="llm_provider").drop(bind, checkfirst=True)
