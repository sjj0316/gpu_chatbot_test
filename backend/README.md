# Fastapi

## 목차

- [1. 설명](#설명)
- [2. 설치](#설치)
- [3. 실행](#실행)
- [4. 폴더 구조](#폴더-구조)

## 설명

- python 3.12 기준으로 작성되었습니다.
- 주요 패키지 : fastapi, langchain, langgraph
- 패키지 관리 : uv
- DB : postgresql 16 (+ pgvector)
  - alembic + sqlalchemy 2.x
    - add migration file :`uv run alembic revision --autogenerate -m "message"`
    - migrate : `uv run alembic upgrade head`

## 빠른 시작 (개발)

- 권장 Python 버전: 3.12
- 권장: `backend/.venv` 가상환경을 사용

1) 가상환경 생성 및 활성화 (Windows PowerShell 예):

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

2) 의존성 설치

```powershell
# dev flow (requirements.txt 사용)
pip install -r requirements.txt

# 또는 uv 사용 시
uv sync
```

3) 환경 변수 예시 (Windows PowerShell)

```powershell
# 예시 — 실제 값은 환경에 맞게 설정하세요
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
$env:DB_NAME = "appdb"
```

4) 데이터베이스 마이그레이션 적용

```powershell
uv run alembic upgrade head
```

5) 개발 서버 실행

```powershell
uv run -m uvicorn app.main:app --reload
# 또는 uvicorn 직접 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 도커 (로컬 개발 - docker-compose)

프로젝트 루트의 `docker-compose.yml`은 개발용 백엔드 이미지를 사용합니다. docker-compose로 전체 스택을 올리면 DB/백엔드/프론트가 함께 실행됩니다.

```powershell
docker compose up --build
```

백엔드가 `backend/Dockerfile.dev-insecure`를 사용하도록 설정되어 있습니다. 이 Dockerfile은 `requirements.txt`로 패키지를 설치하고 `uvicorn`을 실행합니다.

## 테스트 실행

```powershell
# backend 가상환경을 활성화한 뒤
pip install pytest httpx
pytest -q
```


## 설치

### uv 설치

```bash
# https://github.com/astral-sh/uv

# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip.
pip install uv

# Or pipx.
pipx install uv
```

### 파이썬 의존성 패키지 설치

```bash
uv sync
```

## 실행

```bash
uv run -m uvicorn app.main:app --reload
# or
uv run -m uvicorn --host=0.0.0.0 --port 8000 --no-access-log app.main:app --reload

```

## 폴더 구조

```
backend/
├── app/
│    │   main.py                # 애플리케이션 진입점
│    │
│    ├── core/                  # 전역 설정, 예외 처리 등
│    │
│    ├── db/                    # 데이터베이스 연결/세션 관련 (예: SQLAlchemy)
│    │
│    ├── dependencies/          # 의존성 함수
│    │
│    ├── models/                # ORM 모델 정의
│    │
│    ├── routers/               # API 엔드포인트 라우터
│    │
│    ├── schemas/               # Pydantic 스키마
│    │
│    ├── services/               # 비즈니스 로직 처리
│    │
│    └── utils/                 # 공통 헬퍼/유틸리티 함수들
│
├── alembic/ # 데이터베이스 마이그레이션 관리
│
└── tests/ # 테스트 관련
```
