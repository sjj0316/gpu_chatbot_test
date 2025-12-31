"""seed data

Revision ID: ef0e27a04461
Revises: c8281c1ce2d4
Create Date: 2025-08-22 15:03:56.410196

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from passlib.hash import bcrypt

# revision identifiers, used by Alembic.
revision: str = "ef0e27a04461"
down_revision: Union[str, Sequence[str], None] = "c8281c1ce2d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO user_roles (code, label, is_active) VALUES
              ('admin','관리자', true),
              ('user','사용자', true),
              ('system','시스템', true)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO model_providers (code, label, is_active) VALUES
              ('openai','OpenAI', true),
              ('anthropic','Anthropic', true),
              ('google','Google', true),
              ('mistral','Mistral', true),
              ('azure_openai','Azure OpenAI', true),
              ('groq','Groq', true),
              ('local','Local', true),
              ('other','Other', true)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO model_purposes (code, label, is_active) VALUES
              ('chat','Chat', true),
              ('embedding','Embedding', true)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO message_roles (code, label, is_active) VALUES
              ('user','User', true),
              ('assistant','Assistant', true),
              ('tool','Tool', true),
              ('system','System', true)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO message_statuses (code, label, is_active) VALUES
              ('success','Success', true),
              ('error','Error', true),
              ('cancelled','Cancelled', true)
            ON CONFLICT (code) DO NOTHING
            """
        )
    )

    conn.execute(
        sa.text(
            """
        INSERT INTO embedding_specs (provider_id, model, dimension, dtype, is_active)
        VALUES (
            (SELECT id FROM model_providers WHERE code='openai'),
            'text-embedding-3-small', 1536, 'float32', true
        ),
        (
            (SELECT id FROM model_providers WHERE code='openai'),
            'text-embedding-3-large', 3072, 'float32', true
        )
        ON CONFLICT DO NOTHING;
    """
        )
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO users (username, password, nickname, email, role_id)
            VALUES (:u, :p, :n, :e, (SELECT id FROM user_roles WHERE code=:role))
            ON CONFLICT (username) DO NOTHING
            """
        ),
        {"u": "system", "p": "!", "n": "시스템", "e": "system@local", "role": "system"},
    )

    hashed_pw = bcrypt.hash("data123!")
    conn.execute(
        sa.text(
            """
            INSERT INTO users (username, password, nickname, email, role_id)
            VALUES (:u, :p, :n, :e, (SELECT id FROM user_roles WHERE code=:role))
            ON CONFLICT (username) DO NOTHING
            """
        ),
        {
            "u": "admin",
            "p": hashed_pw,
            "n": "관리자",
            "e": "admin@example.com",
            "role": "admin",
        },
    )

    conn.execute(
        sa.text(
            """
            INSERT INTO model_api_keys
              (alias, provider_id, model, endpoint_url, purpose_id, api_key,
               is_public, is_active, owner_id)
            VALUES
              (
                :alias,
                (SELECT id FROM model_providers WHERE code = :provider_code),
                :model,
                :endpoint,
                (SELECT id FROM model_purposes WHERE code = :purpose_code),
                :api_key,
                :is_public,
                :is_active,
                (SELECT id FROM users WHERE username = :owner)
              )
            ON CONFLICT ON CONSTRAINT uq_modelkey_owner_provider_model_endpoint DO NOTHING
            """
        ),
        {
            "alias": "system-openai-embed",
            "provider_code": "openai",
            "model": "text-embedding-3-small",
            "endpoint": None,
            "purpose_code": "embedding",
            "api_key": "",
            "is_public": True,
            "is_active": True,
            "owner": "system",
        },
    )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()

    conn.execute(
        sa.text(
            """
            DELETE FROM model_api_keys
            WHERE alias = :alias
              AND owner_id = (SELECT id FROM users WHERE username = :owner)
            """
        ),
        {"alias": "system-openai-embed", "owner": "system"},
    )

    conn.execute(sa.text("DELETE FROM users WHERE username = :u"), {"u": "admin"})
    conn.execute(sa.text("DELETE FROM users WHERE username = :u"), {"u": "system"})

    conn.execute(
        sa.text(
            "DELETE FROM message_statuses WHERE code IN ('success','error','cancelled')"
        )
    )
    conn.execute(
        sa.text(
            "DELETE FROM message_roles WHERE code IN ('user','assistant','tool','system')"
        )
    )
    conn.execute(
        sa.text("DELETE FROM model_purposes WHERE code IN ('chat','embedding')")
    )
    conn.execute(
        sa.text(
            "DELETE FROM model_providers WHERE code IN ('openai','anthropic','google','mistral','azure_openai','groq','local','other')"
        )
    )
    conn.execute(
        sa.text("DELETE FROM user_roles WHERE code IN ('admin','user','system')")
    )
