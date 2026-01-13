# FastAPI 백엔드

FastAPI 기반 챗봇 백엔드입니다. Python 3.12를 기준으로 개발되었으며 LangChain/LangGraph, SQLAlchemy, Alembic을 사용합니다.

## 1. 요구사항 및 스택

- Python 3.12
- 주요 라이브러리: FastAPI, Uvicorn, LangChain, LangGraph, SQLAlchemy, Alembic
- DB: PostgreSQL 16 (+ pgvector), asyncpg 드라이버
- 패키지 관리자: pip 또는 uv

## 2. 로컬 개발 빠른 시작

1) 가상환경 생성/활성화(PowerShell 예시)

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

2) 의존성 설치

```powershell
# requirements.txt 사용
pip install -r requirements.txt
# 또는 uv 사용
uv sync
```

3) 환경변수 예시(로컬 DB)

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
$env:DB_NAME = "appdb"
```

4) 마이그레이션 적용

```powershell
uv run alembic upgrade head
```

5) 개발 서버 실행

```powershell
uv run -m uvicorn app.main:app --reload
# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 3. Docker Compose 개발 환경

- 루트 `docker-compose.yml`을 사용하면 DB/백엔드/프런트가 함께 기동됩니다.
- 백엔드 서비스는 `backend/Dockerfile`(기본 dev 설정)을 사용합니다.
- 명령어: `docker compose up --build`

## 4. 테스트

```powershell
# 가상환경 활성화 후
pip install pytest httpx
pytest -q
```

## 5. uv 설치 참고

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
# 혹은
pip install uv
```

## 6. 프로젝트 구조

```
backend/
├─ app/               # FastAPI 애플리케이션
│  ├─ core/           # 설정, 공통 처리
│  ├─ db/             # DB 접속/세션 관리
│  ├─ dependencies/   # 의존성 주입
│  ├─ models/         # SQLAlchemy 모델
│  ├─ routers/        # API 라우터
│  ├─ schemas/        # Pydantic 스키마
│  ├─ services/       # 비즈니스 로직
│  └─ utils/          # 유틸리티 함수
├─ alembic/           # 마이그레이션 스크립트
└─ tests/             # 테스트 코드
```
