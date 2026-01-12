"""add wiki pages

Revision ID: 6c2a0c7e9e2a
Revises: acde12345678
Create Date: 2026-01-12 09:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "6c2a0c7e9e2a"
down_revision: Union[str, Sequence[str], None] = "acde12345678"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "wiki_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "is_public", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column("updated_by_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), onupdate=sa.func.now(), nullable=True
        ),
    )
    op.create_index(op.f("ix_wiki_pages_slug"), "wiki_pages", ["slug"], unique=True)
    op.create_index(
        op.f("ix_wiki_pages_is_public"), "wiki_pages", ["is_public"], unique=False
    )
    op.create_index(
        op.f("ix_wiki_pages_updated_by_id"),
        "wiki_pages",
        ["updated_by_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_wiki_pages_updated_by_users",
        "wiki_pages",
        "users",
        ["updated_by_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.execute(
        sa.text(
            """
            INSERT INTO wiki_pages (slug, title, content, is_public)
            VALUES (:slug, :title, :content, true)
            """
        ).bindparams(
            slug="guide",
            title="BD 챗봇 사용 가이드",
            content=(
                "# BD 챗봇 사용 가이드\n\n"
                "이 문서는 BD 챗봇 서비스의 전반적인 사용 방법을 안내합니다. "
                "항목별 핵심 흐름과 주의사항을 간략히 정리했습니다.\n\n"
                "## 시작하기\n\n"
                "- 로그인 후 좌측 메뉴에서 각 기능으로 이동합니다.\n"
                "- 상단 사용자 메뉴에서 프로필/비밀번호 변경을 할 수 있습니다.\n"
                "- 홈 화면의 카드에서 주요 기능으로 바로 이동할 수 있습니다.\n\n"
                "## 대화하기\n\n"
                "- 대화를 만들고, 모델 키를 선택한 뒤 질문을 입력하세요.\n"
                "- 기본 API 키를 선택하면 이후 대화 생성에 기본값으로 유지됩니다.\n"
                "- MCP 서버를 선택하면 추가 도구/연결을 활용할 수 있습니다.\n\n"
                "## 컬렉션 관리\n\n"
                "- 문서를 묶는 단위를 컬렉션이라고 합니다.\n"
                "- 컬렉션을 먼저 만든 뒤 문서를 업로드하세요.\n"
                "- 공개 여부를 설정하면 다른 사용자에게 공유할 수 있습니다.\n\n"
                "## 문서 관리\n\n"
                "- 업로드 전 컬렉션을 반드시 선택해야 합니다.\n"
                "- 청크 크기와 오버랩은 검색 품질에 영향을 줍니다.\n"
                "- 메타데이터(JSON)를 입력하면 문서 검색/분류에 활용됩니다.\n\n"
                "## 모델 키(API 키) 관리\n\n"
                "- 임베딩/대화 목적에 맞는 API 키를 등록하세요.\n"
                "- 비활성화된 키는 선택 목록에서 제외됩니다.\n"
                "- 보안상 공개 여부를 신중히 설정하세요.\n\n"
                "## MCP 서버\n\n"
                "- 외부 도구/서버를 연결해 확장 기능을 사용할 수 있습니다.\n"
                "- 사용 권한은 관리자 정책에 따라 제한될 수 있습니다.\n\n"
                "## 프로필/보안\n\n"
                "- 프로필에서 닉네임과 이메일을 수정할 수 있습니다.\n"
                "- 비밀번호 변경은 현재 비밀번호 확인 후 진행됩니다.\n"
                "- 계정 보안을 위해 주기적으로 비밀번호를 변경하세요.\n\n"
                "## 문제 해결\n\n"
                "- 업로드 실패: 컬렉션 선택 여부와 파일 형식을 확인하세요.\n"
                "- 로그인 실패: 아이디/비밀번호 확인 후 다시 시도하세요.\n"
                "- API 키 오류: 활성화 여부와 권한을 확인하세요.\n"
            ),
        )
    )


def downgrade() -> None:
    op.drop_constraint("fk_wiki_pages_updated_by_users", "wiki_pages", type_="foreignkey")
    op.drop_index(op.f("ix_wiki_pages_updated_by_id"), table_name="wiki_pages")
    op.drop_index(op.f("ix_wiki_pages_is_public"), table_name="wiki_pages")
    op.drop_index(op.f("ix_wiki_pages_slug"), table_name="wiki_pages")
    op.drop_table("wiki_pages")
