# BD Chatbot 프로젝트

React(프런트엔드) + FastAPI(백엔드) + PostgreSQL(pgvector) 기반의 챗봇 서비스입니다. 루트, 백엔드, 프런트엔드 각각의 README를 참고해 주세요.

## 주요 스택

- **Frontend:** React, Vite, TanStack Query, Ky, Zustand, shadcn/ui(Tailwind v4)
- **Backend:** FastAPI, LangChain, LangGraph, Uvicorn, SQLAlchemy, Alembic
- **Database:** PostgreSQL 16 + pgvector

## 1단계: Docker Compose로 빠른 실행(권장)

루트의 `docker-compose.yml`과 `.env`를 사용하면 DB/백엔드/프런트가 한 번에 올라갑니다.

```powershell
docker compose up --build
```

- Backend: http://localhost:8000 (Swagger: `/docs`)
- Frontend: http://localhost (기본 80 포트, Vite dev 서버는 http://localhost:5173)
- DB: 호스트 `127.0.0.1`, 포트 `15432`로 노출

## 2단계: 데이터베이스 마이그레이션(Docker DB 기준)

로컬 가상환경에서 Alembic을 실행할 때는 Docker DB 포트/계정을 명시합니다.

```powershell
$env:POSTGRES_HOST='127.0.0.1'
$env:POSTGRES_PORT='15432'
$env:POSTGRES_USER='app_user'
$env:POSTGRES_PASSWORD='app_password'
$env:POSTGRES_DB='app_db'
backend\.venv\Scripts\python -m alembic -c backend\alembic.ini upgrade head
backend\.venv\Scripts\python -m alembic -c backend\alembic.ini current
```

## 3단계: 백엔드 로컬 개발(Python)

1) 가상환경 생성 및 활성화(PowerShell 예시)

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

2) 의존성 설치

```powershell
# requirements.txt 사용
pip install -r backend\requirements.txt
# 또는 uv 사용
uv sync
```

3) 필수 환경변수 예시

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

## 4단계: 프런트엔드 로컬 개발

```powershell
cd frontend
pnpm install # 또는 npm install, yarn install
pnpm run dev
```

API 엔드포인트를 바꾸려면 `frontend/.env`에 `VITE_API_BASE_URL`을 설정합니다.

## 5단계: 테스트

백엔드 pytest 실행 예시:

```powershell
cd backend
pip install pytest httpx
pytest -q
```

## RAG/임베딩 주의

- 문서 업로드/검색은 유효한 임베딩 API Key가 필요합니다.
- 임베딩 키가 없으면 관련 엔드포인트가 HTTP 400(`api_key required`)을 반환합니다.

## 추가 문서

- 백엔드 상세: `backend/README.md`
- 프런트엔드 상세: `frontend/README.md`
