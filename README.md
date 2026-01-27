# BD Chatbot 프로젝트

React(프런트엔드) + FastAPI(백엔드) + PostgreSQL(pgvector) 기반의 챗봇 서비스입니다. 루트, 백엔드, 프런트엔드 각각의 README를 참고해 주세요.

## 주요 스택

- **프론트엔드:** React, Vite, TanStack Query, Ky, Zustand, shadcn/ui(Tailwind v4)
- **백엔드:** FastAPI, LangChain, LangGraph, Uvicorn, SQLAlchemy, Alembic
- **데이터베이스:** PostgreSQL 16 + pgvector

## 1단계: Docker Compose로 빠른 실행(권장)

루트의 `docker-compose.yml`과 `.env`를 사용하면 DB/백엔드/프런트가 한 번에 올라갑니다.

```powershell
docker compose up --build
```

- 백엔드: http://localhost:8000 (Swagger: `/docs`)
- 프론트엔드: http://localhost (기본 80 포트, Vite dev 서버는 http://localhost:5173)
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
$env:POSTGRES_HOST = "localhost"
$env:POSTGRES_PORT = "5432"
$env:POSTGRES_USER = "postgres"
$env:POSTGRES_PASSWORD = "postgres"
$env:POSTGRES_DB = "appdb"
# 또는 DATABASE_URL로 일괄 설정
$env:DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/appdb"
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
pip install pytest pytest-asyncio httpx
pytest -q
```

## RAG/임베딩 주의

- 문서 업로드/검색은 **model_api_keys에 등록된 임베딩 API Key**가 필요합니다.
- 키가 비어 있으면 관련 엔드포인트가 HTTP 400을 반환합니다(예: `OpenAIEmbeddings: api_key가 필요합니다.`).

## 추가 문서

- 백엔드 상세: `backend/README.md`
- 프런트엔드 상세: `frontend/README.md`

## 운영 배포 패키지(사내망 Docker Compose)

이 레포에는 사내망 서버에서 Docker Compose로 운영할 때 사용하는 **런북/템플릿**이 포함돼 있습니다.
서버 로컬 Build와 `.env.prod` 주입을 전제로 하며, 아래 파일을 참고하세요.

- `docker-compose.prod.yml` (운영용 compose 골격)
- `.env.sample` (키 목록 표준, 값 없음)
- `scripts/preflight_all.ps1` (Windows preflight 진입점)

운영 리허설 경로(서버에서 `.env.prod`를 채운 뒤):

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml config
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 테스트 계정

id : admin
pw : data123!

## 프로젝트 구조(루트 기준)

폴더
- `backend` : FastAPI 백엔드
- `frontend` : React 프론트엔드
- `db` : 데이터베이스 관련 파일/리소스
- `nginx` : Nginx 설정
- `ops` : 운영 문서/템플릿
- `scripts` : 운영 preflight 스크립트
- `.vscode` : 에디터 설정

파일
- `docker-compose.yml` : 로컬/기본 compose

    다음 파일의 경우 임의 생성
    - `docker-compose.prod.yml` : 운영 compose
    - `docker-compose.test.yml` : 테스트 compose
    - `docker-compose.yml.backup` : 이전 compose 백업


- `.env` : 로컬 환경 변수(값 포함 가능, 커밋 금지)
- `.env.sample` : 키 목록 표준(값 없음)
- `.dockerignore` : Docker 빌드 제외 규칙
- `.gitignore` : Git 제외 규칙
- `.gitlab-ci.yml` : CI 설정 파일(사용 여부는 운영 정책에 따름)
- `frontend-backend-mapping.md` : 프론트/백엔드 매핑 문서
- `Makefile` : 운영/검증 명령 모음
- `README.md` : 프로젝트 개요
- `seed_ui_demo.sql` : UI 데모용 시드 SQL
