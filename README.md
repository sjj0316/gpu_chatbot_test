# Start Project

- **frontend:** react
- **backend:** fastapi
- **database:** postgresql 16 + pgvector extension

frontend/README.md
backend/README.md
를 참고하세요


<!-- 추가 

[AWS EC2 public ip] 
	http://15.165.48.80
	현재 생성된 테스트용 사용자 계정
	id : admin
	pw : data123!
	
	
[DB 정보]
	host : ds-team-db-cluster.cluster-cdwjlhjzkkua.ap-northeast-2.rds.amazonaws.com
	port : 5432
	user : dsteam
	password : dataservice12#
	db : dschat


[프론트에서 백엔드 연결가이드]
	frontend/.env 파일 생성
	VITE_API_BASE_URL=http://15.165.48.80

	이후 vite 개발서버 실행
	pnpm run dev

[백엔드 Swagger]
	http://15.165.48.80/docs
	http://15.165.48.80/redoc
	만료 없는 api key :  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVpZCI6Miwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzU2Njk2OTY4LCJzY29wZSI6WyJyYWcucmVhZCIsInJhZy5zZWFyY2giXX0._b5jV-Twguno9KaXVqg3XT4W_hrVwKXJVSzZFYDqk2Q

[gitlab 작업]
	권장 : origin/dev 기준으로 branch 생성하여 작업 후 PR

[CI/CD]
	"main" branch push 시에 자동으로 pipeline이 작동됩니다.
	"ec2 ssh 접속 -> git pull -> docker build -> docker deploy"
 -->

## Quick start (recommended: Docker Compose)

프로젝트 루트에 있는 `docker-compose.yml`을 사용하면 DB, backend(dev), frontend를 한 번에 띄울 수 있습니다.

```powershell
docker compose up --build
```

- Backend: http://localhost:8000 (Swagger: /docs)
- Frontend: Vite가 사용하는 포트(예: http://localhost:5173)

## 로컬 개발 (Python 환경)

1) `backend`에서 가상환경 생성 및 활성화(Windows PowerShell 예):

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

2) 의존성 설치:

```powershell
# 권장: requirements.txt 사용
pip install -r backend\requirements.txt

# 또는 uv 사용 시
uv sync
```

3) 환경변수 설정(예):

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
$env:DB_USER = "postgres"
$env:DB_PASSWORD = "postgres"
$env:DB_NAME = "appdb"
```

4) 마이그레이션 적용:

```powershell
uv run alembic upgrade head
```

5) 개발 서버 실행:

```powershell
uv run -m uvicorn app.main:app --reload
# 또는
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6) 프론트 개발 서버:

```powershell
cd frontend
pnpm install # 또는 npm install
pnpm run dev
```

## 테스트 실행

Backend pytest 예시:

```powershell
cd backend
# 가상환경 활성화 후
pip install pytest httpx
pytest -q
```

## 노트

- 프로젝트는 `backend/.venv`를 권장합니다.
- 민감 정보(패스워드, 토큰)는 저장소에 커밋하지 마시고 `.env` 또는 환경변수를 사용하세요.
