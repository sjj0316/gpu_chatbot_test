# 운영 배포 절차(사내망 Docker Compose)

## 0. 전제 및 범위

* [운영전제] 배포 대상: 사내망 내부 서버
* [운영전제] 배포 방식: Docker Compose 기반
* [운영전제] 배포 흐름: 서버 로컬 Build(서버에서 이미지 빌드 후 compose up)
* [운영전제] 운영 env 정책: .env.prod 단일 파일(서버 로컬에만 존재, 커밋 금지)
* [운영전제] 프록시 경로: Nginx가 /api/ 를 backend로 프록시, smoke/health는 /api/openapi.json으로 확인
* [레포근거] 루트 .env.sample 존재(키 목록 표준)
* [레포근거] 하위 샘플 env 존재: backend/app/core/.env.sample(개발 참고용)
* [운영전제] 배포 기록은 ops/release.log 가 단일 소스(Source of Truth)

> 본 문서는 로컬 개발 단계에서도 운영으로 넘어가기 위한 최소 표준(문서/절차/검증)을 고정한다.

---

## 1) P0-DEP-1 운영용 Compose 분리/고정

### 1.1 산출물(운영 패키지)

* docker-compose.prod.yml (운영 전용)
* ops/deploy.md (본 문서)
* ops/release.log (배포 기록 단일 소스, 커밋 금지)
* ops/release.log.template (배포 기록 템플릿, 커밋 대상)
* .env.prod (운영 실값, 서버에만 존재, 커밋 금지)
* .env.sample (키 목록 표준, 값 없음, 커밋 가능)
* scripts/preflight_env.* (필수 env 키 존재 검사 스크립트, 값 출력 금지)
* (선택) Makefile (표준 배포 명령)

### 1.2 운영 Compose 공통 원칙

* 이미지 태그 고정: backend:<TAG>, frontend:<TAG>, db:<TAG>
* restart 정책: restart: unless-stopped
* healthcheck 필수: db, backend, nginx(frontend) 모두 설정
* depends_on: 최소 backend -> db(healthy) 순서로 강제
* 운영 데이터는 named volume로 분리
* 운영 env는 .env.prod로만 주입(env_file: .env.prod)
* 운영에서는 .env.sample을 참조하지 않는다(키 목록 표준이므로)

---

## 2) Healthcheck 표준(구체 명령, 운영 실패 감소용)

> 중요: healthcheck는 컨테이너 내부에서 실행되므로, 이미지에 포함된 도구만 사용한다.

### 2.1 DB (Postgres + pgvector)

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 6
  start_period: 20s
```

### 2.2 Backend (FastAPI)

* 코드 수정 없이 기준 엔드포인트: GET /openapi.json
* 도구 의존성 최소화: python urllib 사용

```yaml
healthcheck:
  test:
    [
      "CMD-SHELL",
      "python -c \"import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/openapi.json', timeout=3).read();\""
    ]
  interval: 10s
  timeout: 5s
  retries: 6
  start_period: 30s
```

### 2.3 Nginx / Frontend (정적 서빙 + 프록시)

* 정적 서빙 확인: GET /
* 프록시 확인(운영 권장): GET /api/openapi.json

```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://127.0.0.1/ >/dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 6
  start_period: 20s
```

```yaml
# 선택(운영 권장): 프록시 확인
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://127.0.0.1/api/openapi.json >/dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 6
  start_period: 30s
```

---

## 3) P0-DEP-3 시크릿 주입/환경 분리 정책(단일 규칙 고정)

### 3.1 단일 규칙

* 운영 실값은 .env.prod로만 관리한다(서버 로컬 파일).
* .env.prod는 커밋 금지, 접근 권한 최소화.
* .env.sample은 키 목록 표준이다(값 없음/더미만, 커밋 가능).
* 운영 경로에서 backend/app/core/.env.sample을 참조하지 않는다(혼선 방지).

### 3.2 서버 권한(권장)

```bash
chmod 600 .env.prod
```

### 3.3 Preflight에서의 env 키 검증(값 노출 금지)

* 기준: 루트 .env.sample의 키 목록
* 대상: .env.prod 또는 서버 환경변수
* 출력: 누락된 키 이름만 출력(값 절대 출력 금지)

---

## 4) P0-DEP-2 배포 절차 표준(서버 로컬 Build)

### 4.1 배포 전 준비(Preflight 포함)

1. 서버에 코드 반영(예: git pull 또는 배포 패키지 반영)
2. <TAG> 결정(태그 표준은 아래 8절 참조)
3. preflight 실행(필수)
4. build → up → health → smoke test 순서로 진행
5. 배포 기록을 ops/release.log에 남긴다(필수)

### 4.2 운영 리허설 커맨드(표준)

```bash
# 1) compose 유효성
docker compose --env-file .env.prod -f docker-compose.prod.yml config

# 2) 기동(로컬 build)
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build

# 3) 상태/로그
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200
```

---

## 5) Preflight 체크리스트(배포 실패를 앞당기는 강제 게이트)

### 5.1 목적

배포 전에 필수 파일/키/compose 유효성을 강제하여 운영 실패를 사전에 차단한다.

### 5.2 필수 검사 항목(최소)

1. compose config 유효성

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml config
```

2. 필수 env 키 존재 여부(값 노출 금지)

* .env.sample의 키 목록을 기준으로 .env.prod에 존재 여부만 확인한다.

3. 이미지 태그 규칙 확인

* <TAG> 규칙이 문서(8절)와 일치하는지 확인
* 배포 기록에 <TAG>를 남길 준비가 되었는지 확인

### 5.3 Preflight 실행 규칙(문서 고정 문구)

* preflight 실패 시 배포 명령은 non-zero로 종료되어 up이 실행되지 않는다.
* 포함 항목: compose config + 필수 env 키 존재 체크 + 태그 규칙 체크.

### 5.4 검증 전용 config 체크(로컬/문서 검증용)

```bash
docker compose --env-file .env.sample -f docker-compose.prod.yml config
```

### 5.5 운영 리허설/실배포 경로(운영 표준)

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml config
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

### 5.6 Windows PowerShell 기본 경로(권장)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/preflight_all.ps1
powershell -ExecutionPolicy Bypass -File scripts/preflight_env.ps1
```

* bash가 없는 환경에서 scripts/preflight_env.sh 실행 실패는 정상이다.
* Linux 서버/WSL 환경에서만 scripts/preflight_env.sh를 사용한다.

---

## 6) 운영 1회 리허설 런북(사내 서버 기준)

### 6.1 목적

운영 전 “1회 재현 가능한 성공”을 확보한다. (로컬/사내망 서버 모두 동일)

### 6.2 준비(.env.prod + TAG)

```powershell
Copy-Item .env.sample .env.prod
# .env.prod를 열어서 값 채우기
notepad .env.prod
```

* 운영 값은 서버에서만 입력하고 커밋하지 않는다.
* TAG는 배포 단위를 나타내며 backend/frontend/db에 동일하게 적용한다.

### 6.3 리허설 커맨드 세트(운영 표준)

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml config
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 6.4 Preflight 실행(권장)

```powershell
powershell -ExecutionPolicy Bypass -File scripts/preflight_all.ps1
```

### 6.5 Smoke Test(필수)

```powershell
curl -fsS http://localhost/ | Out-Null
curl -fsS http://localhost/api/openapi.json | Out-Null
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 6.6 Quiet 모드(민감값 노출 최소화, 옵션)

* stdout만 억제하고 실패는 감지한다.

```powershell
docker compose --env-file .env.sample -f docker-compose.prod.yml config | Out-Null
if ($LASTEXITCODE -ne 0) { throw "compose config failed" }
```

---

## 7) Smoke Test 최소 체크리스트(운영 배포 직후 3~5분)

### 6.1 목적

운영 배포 직후 3~5분 내 최소 기능 생존을 확인하고, 실패 시 원인을 즉시 분류한다.

### 6.2 체크 항목(필수, 3분)

1. Frontend 정적 서빙

```bash
curl -fsS http://localhost/ >/dev/null
```

2. Backend API 프록시(Nginx → Backend)

```bash
curl -fsS http://localhost/api/openapi.json >/dev/null
```

3. 컨테이너 상태(기동/헬스)

```bash
docker compose -f docker-compose.prod.yml ps
```

4. 최근 로그(장애 징후)

```bash
docker compose -f docker-compose.prod.yml logs --tail=120
```

### 6.3 선택(권장, 권한 필요 시 1~2분)

5. RAG 기본 엔드포인트(권한 필요)

```bash
curl -fsS -H "Authorization: Bearer ***" http://localhost/api/v1/collections >/dev/null
```

* 토큰/키는 반드시 마스킹한다.
* 실패 시 인증(401/403) vs API 장애(5xx/timeout)로 구분한다.

### 6.4 실패 시 즉시 분기(30초 원인 분류)

* curl http://localhost/ 실패 → nginx/frontend 기동/포트/정적파일 문제 가능성
* curl http://localhost/api/openapi.json 실패(단 /는 성공) → 프록시 경로/백엔드/네트워크 문제 가능성
* ps에서 unhealthy 존재 → 해당 서비스 로그 우선

```bash
docker compose -f docker-compose.prod.yml logs <service> --tail=200
```

---

## 8) 이미지 태그 규칙(운영 표준) + 기록 위치 고정(release.log)

### 7.1 태그 규칙(단일 배포 단위)

* <TAG>는 운영 배포 단위를 나타낸다.
* <TAG>는 단일 배포에서 backend/frontend/db에 동일하게 적용한다(동일 TAG 강제).
* 표준 형식(문서에서 1개로 고정):

  * 날짜형: YYYY.MM.DD
  * 또는 커밋형: git short SHA

### 7.2 운영 표준 예시

* backend:2026.01.14
* frontend:2026.01.14
* db:2026.01.14

### 7.3 롤백 표준

* 롤백은 직전 <TAG_PREV>로의 재기동을 표준으로 한다.
* <TAG_PREV>는 배포 전 직전 배포 태그로 사전에 확인한다.

### 7.4 TAG 기록 위치(단일 소스 고정)

* 배포 기록은 ops/release.log에 남긴다(필수).
* ops/release.log.template을 복사해 ops/release.log로 사용한다.
* 최소 기록 필드(권장):

  * 날짜/시간
  * TAG
  * git SHA(가능하면)
  * 작업자
  * 결과(SUCCESS/FAIL)
  * 비고(장애/롤백 여부)

예시:

```
2026-01-14 11:30 KST | TAG=2026.01.14 | SHA=abc1234 | OP=BD | RESULT=SUCCESS | NOTE=smoke ok
2026-01-15 09:10 KST | TAG=2026.01.15 | SHA=def5678 | OP=BD | RESULT=FAIL | NOTE=backend unhealthy -> rollback to 2026.01.14
```

---

## 9) 롤백 절차(최소 전략)

1. ops/release.log에서 직전 성공 TAG(<TAG_PREV>) 확인
2. compose가 참조하는 이미지 태그를 <TAG_PREV>로 맞춘 뒤 재기동
3. healthcheck + smoke test 재검증
4. DB 마이그레이션이 비가역이면(다운 불가) 해당 사실을 ops/release.log에 기록

---

## 10) P0-DEP-4 게이트(사내 CI 또는 대체 게이트)

* CI/CD가 없더라도 배포 품질을 강제해야 한다.
* 기본 원칙: 배포는 preflight를 반드시 선행하며 실패 시 중단한다.
* 현재 단계(사내망/로컬 개발): 수동 게이트 + release.log 증빙을 운영 표준으로 유지한다.
* 향후 가능 시: GitHub Actions 또는 사내 CI로 lint/test 게이트를 추가한다(옵션).

---

## 11) 변경 이력

* (작성자가 기록) 날짜 / 변경 요약 / 승인(있으면)
