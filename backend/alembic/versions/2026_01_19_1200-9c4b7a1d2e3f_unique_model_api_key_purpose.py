"""Adjust model_api_keys uniqueness to include purpose_id.

Revision ID: 9c4b7a1d2e3f
Revises: 8f1e9b4d2c3a
Create Date: 2026-01-19 12:00:00.000000
"""

from alembic import op

revision = "9c4b7a1d2e3f"
down_revision = "8f1e9b4d2c3a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("model_api_keys") as batch:
        batch.drop_constraint(
            "uq_modelkey_owner_provider_model_endpoint", type_="unique"
        )
        batch.create_unique_constraint(
            "uq_modelkey_owner_provider_model_purpose",
            ["owner_id", "provider_id", "model", "purpose_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("model_api_keys") as batch:
        batch.drop_constraint(
            "uq_modelkey_owner_provider_model_purpose", type_="unique"
        )
        batch.create_unique_constraint(
            "uq_modelkey_owner_provider_model_endpoint",
            ["owner_id", "provider_id", "model", "endpoint_url"],
        )
