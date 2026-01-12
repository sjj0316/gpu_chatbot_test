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
	pw : ********
	
	
[DB 정보]
	host : ds-team-db-cluster.cluster-cdwjlhjzkkua.ap-northeast-2.rds.amazonaws.com
	port : 5432
	user : dsteam
	password : ********
	db : dschat


[프론트에서 백엔드 연결가이드]
	frontend/.env 파일 생성
	VITE_API_BASE_URL=http://15.165.48.80

	이후 vite 개발서버 실행
	pnpm run dev

[백엔드 Swagger]
	http://15.165.48.80/docs
	http://15.165.48.80/redoc
	만료 없는 api key :  ********

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

## Database migrations (Docker Compose DB)

When using the provided `docker-compose.yml`, the DB listens on host port `15432`.
Run Alembic from the local virtualenv with explicit DB env vars:

```powershell
$env:POSTGRES_HOST='127.0.0.1'
$env:POSTGRES_PORT='15432'
$env:POSTGRES_USER='app_user'
$env:POSTGRES_PASSWORD='app_password'
$env:POSTGRES_DB='app_db'
backend\.venv\Scripts\python -m alembic -c backend\alembic.ini upgrade head
```

Check current migration version:

```powershell
backend\.venv\Scripts\python -m alembic -c backend\alembic.ini current
```

## 로컬 개발 (Python 환경)

1) `backend`에서 가상환경 생성 및 활성화(Windows PowerShell 예):

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

2) 의존성 설치:

```powershell
# requirements.txt 사용
pip install -r backend\requirements.txt

# 권장 : uv 사용
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

## RAG testing note

- Document upload/search requires a valid embedding API key.
- Without a valid embedding API key, endpoints return HTTP 400 with an "api_key required" message.

## API 키 등록 입력 예시(엔드포인트 안내)

### 1) 엔드포인트 URL이 달라서 실패하는 대표 케이스

#### A. 같은 OpenAI 플랫폼 내에서도 경로(path)가 다르면 동작이 다릅니다

- Chat Completions: `POST https://api.openai.com/v1/chat/completions` ([OpenAI 플랫폼][2])
- Responses: `POST https://api.openai.com/v1/responses` ([OpenAI 플랫폼][3])
- OpenAI 문서에서도 `/v1/chat/completions` -> `/v1/responses`로 엔드포인트 업데이트를 명시합니다. ([OpenAI 플랫폼][4])

```bash
# (실패 예시) 응답 생성 로직인데 chat/completions로 잘못 호출 + payload도 responses 방식(input)을 보냄
curl -s https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": [{"role":"user","content":"Hello"}]
  }'

# (정상 예시) 같은 payload를 responses 엔드포인트로 호출
curl -s https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": [{"role":"user","content":"Hello"}]
  }'
```

#### B. OpenAI vs Azure OpenAI는 호스트(베이스 URL) + 경로 규칙이 다릅니다

- Azure OpenAI는 리소스별 엔드포인트와 deployment-id, api-version 쿼리를 요구합니다. ([Microsoft Learn][5])
- 예: `POST https://{YOUR_RESOURCE_NAME}.openai.azure.com/openai/deployments/{YOUR_DEPLOYMENT_NAME}/chat/completions?api-version=...` ([Microsoft Learn][5])

```bash
# (Azure 정상 예시)
curl -s "https://YOUR_RESOURCE_NAME.openai.azure.com/openai/deployments/YOUR_DEPLOYMENT_NAME/chat/completions?api-version=2024-06-01" \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_OPENAI_API_KEY" \
  -d '{
    "messages": [{"role":"user","content":"Hello"}]
  }'
```

#### C. 일반 OpenAI API 키는 Bearer 인증 + api.openai.com 사용

OpenAI API 레퍼런스는 인증을 HTTP Bearer로 안내하고, 예시로 `https://api.openai.com/v1/models` 호출을 제공합니다. ([OpenAI 플랫폼][1])

```bash
curl -s https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### 2) OpenAI API Key 기준 엔드포인트 예시

1) Responses: `POST https://api.openai.com/v1/responses` ([OpenAI 플랫폼][3])

```bash
curl -s https://api.openai.com/v1/responses \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "input": [{"role":"user","content":"Summarize this."}]
  }'
```

2) Chat Completions(레거시/호환): `POST https://api.openai.com/v1/chat/completions` ([OpenAI 플랫폼][2])

```bash
curl -s https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role":"user","content":"Hello"}]
  }'
```

3) Embeddings: `POST https://api.openai.com/v1/embeddings` ([OpenAI 플랫폼][6])

```bash
curl -s https://api.openai.com/v1/embeddings \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "임베딩 테스트 문장"
  }'
```

[1]: https://platform.openai.com/docs/api-reference/introduction "API Reference - OpenAI API"
[2]: https://platform.openai.com/docs/api-reference/chat "Chat Completions | OpenAI API Reference"
[3]: https://platform.openai.com/docs/api-reference/responses "Responses | OpenAI API Reference"
[4]: https://platform.openai.com/docs/guides/migrate-to-responses "Migrate to the Responses API | OpenAI API"
[5]: https://learn.microsoft.com/en-us/azure/ai-foundry/openai/reference?view=foundry-classic "Azure OpenAI in Microsoft Foundry Models REST API reference - Azure OpenAI | Microsoft Learn"
[6]: https://platform.openai.com/docs/api-reference/embeddings "Embeddings | OpenAI API Reference"

## 노트

- 프로젝트는 `backend/.venv`를 권장합니다.
- 민감 정보(패스워드, 토큰)는 저장소에 커밋하지 마시고 `.env` 또는 환경변수를 사용하세요.
