# 인수인계 문서(Template) — BD Chatbot

> 목적: 새 담당자가 **빠르게 실행/운영/개발**할 수 있도록 필수 정보를 한 곳에 정리합니다.
> 작성 범위: 사내망 Docker Compose 운영 + 로컬 개발 + 핵심 기능.

---

## 0. 요약(한 눈에 보기)
- 서비스 목적: (한 문장으로 기입)
- 사용자 범위: 사내망 내부 사용자 (외부 공개 여부: □예 / ■아니오)
- 핵심 기능 3줄:  
  1) RAG 기반 문서 검색/챗봇  
  2) 모델 API 키 관리  
  3) MCP 서버 연동

---

## 1. 아키텍처 개요
### 1.1 구성 요소
- Frontend: React + Vite (정적 빌드 → Nginx)
- Backend: FastAPI (API)
- DB: PostgreSQL 16 + pgvector
- Proxy: Nginx

### 1.2 네트워크 흐름
- 브라우저 → Nginx(80) → `/api/*` → Backend(8000)
- Backend → Postgres(5432 in compose)

### 1.3 핵심 포트/URL
- Frontend: http://localhost
- Backend: http://localhost:8000 (`/docs`, `/openapi.json`)
- Proxy Health: http://localhost/api/openapi.json
- DB: 127.0.0.1:15432 (로컬 compose 기준)

---

## 2. 실행 방법
### 2.1 Docker Compose (권장)
```powershell
docker compose up --build
```

### 2.2 로컬 개발(백엔드)
```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
uv run alembic upgrade head
uv run -m uvicorn app.main:app --reload
```

### 2.3 로컬 개발(프론트엔드)
```powershell
cd frontend
pnpm install
pnpm run dev
```

---

## 3. 환경변수/시크릿
### 3.1 기본 정책
- 샘플 키: `.env.sample`
- 운영 키: `.env.prod` (서버에만 존재, 커밋 금지)

### 3.2 필수 키(요약)
- DB: `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`
- 인증: `JWT_SECRET_KEY`, `ACCESS_TOKEN_EXPIRE`, `REFRESH_TOKEN_EXPIRE`
- 모델: `OPENAI_API_KEY`, `LANGCHAIN_API_KEY`, `LANGCHAIN_ENDPOINT`  
  (실제 사용 경로는 model_api_keys 기준 — 상세는 5절)

---

## 4. 배포/운영(사내망 Docker Compose)
### 4.1 운영 런북
- 문서: `ops/deploy.md`
- 기록: `ops/release.log` / 템플릿 `ops/release.log.template`

### 4.2 표준 절차
1) Preflight  
2) Build & Up  
3) Healthcheck  
4) Smoke Test  
5) release.log 기록

### 4.3 Smoke Test
```bash
curl -fsS http://localhost/ >/dev/null
curl -fsS http://localhost/api/openapi.json >/dev/null
```

---

## 5. 인증/인가
### 5.1 토큰 흐름
- `/api/v1/auth/login` → access/refresh 발급  
- `/api/v1/auth/refresh` → 재발급  
- 프론트는 `localStorage`에 토큰 저장

### 5.2 권한 정책
- 일반 사용자: 소유 리소스만 접근
- 관리자: 전체 접근 (`admin`/`system`)

### 5.3 기본 계정(시드)
- admin / data123!  (alembic 시드로 생성됨)

---

## 6. DB / 마이그레이션
### 6.1 마이그레이션
```powershell
uv run alembic upgrade head
```

### 6.2 초기 데이터
- `alembic/versions/2025_08_22_1503-ef0e27a04461_seed_data.py`  
  (role/provider/purpose/admin 계정 포함)

---

## 7. 주요 기능 매핑(요약)
| 기능 | API 엔드포인트 | 비고 |
|---|---|---|
| 로그인 | `POST /api/v1/auth/login` | 토큰 발급 |
| 대화 | `/api/v1/conversations/*` | invoke/stream |
| RAG | `/api/v1/collections/*` | 문서 업로드/검색 |
| 모델 키 | `/api/v1/api-keys/*` | 키 등록/조회 |
| MCP 서버 | `/api/v1/mcp-servers/*` | 외부 도구 |
| 위키 | `/api/v1/wiki/*` | 안내 문서 |

---

## 8. 프론트엔드 구조
- FSD 구조: `src/app`, `pages`, `widgets`, `features`, `entities`, `shared`
- 라우팅: `frontend/src/app/router/app-router.tsx`

---

## 9. 테스트
```powershell
cd backend
pip install pytest pytest-asyncio httpx
pytest -q
```

---

## 10. 알려진 리스크/기술 부채
- (TODO) 이슈/리스크 목록 기입

---

## 11. 인수인계 체크리스트
- [ ] 로컬 실행 성공
- [ ] 운영 배포 리허설 1회 수행
- [ ] smoke test 통과
- [ ] release.log 작성
- [ ] 계정/권한 정책 숙지
- [ ] 모델 키 등록/문서 업로드 테스트

---

## 12. 변경 이력
- 날짜 / 변경 요약 / 작성자 / 승인자
