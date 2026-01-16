# 운영 배포 절차(사내망 Docker Compose)

이 문서는 **사내망 내부 서버**에서 Docker Compose로 서비스를 배포/롤백할 때, 실패를 일찍 발견하고(Preflight/Healthcheck) 기록을 남기기(release.log) 위한 **런북(runbook)**입니다.

---

## 0. 전제와 범위

- 배포 대상: 사내망 내부 서버(외부 인터넷 공개가 아님)
- 배포 방식: Docker Compose
- 빌드 방식: **서버 로컬 Build**
- 프록시 경로: **/api/** → backend, Smoke/Health 기준 경로는 **/api/openapi.json**
- 시크릿 주입: **.env.prod 파일 방식**(레포에는 샘플 키 목록만 유지)

> 참고: 레포에는 개발 참고용 `.env.sample`이 `backend/app/core/.env.sample`에 존재했습니다. 운영 표준은 **루트 `.env.sample`(키 목록만)** + **서버의 `.env.prod`(실제 값)** 입니다.

---

## 1. 운영 배포 패키지 구성(필수 파일)

| 구분 | 파일 | 목적 | 위치/비고 |
|---|---|---|---|
| 운영 compose | `docker-compose.prod.yml` | 운영용 설정(healthcheck, restart, env 정책, 포트 정책) | 레포 루트 |
| 키 목록 샘플 | `.env.sample` | **키 이름만**(값 없음) | 레포 루트(커밋 가능) |
| 운영 시크릿 | `.env.prod` | **실제 값** | 서버에만 존재(커밋 금지) |
| 운영 절차 | `deploy.md` | 배포/롤백/리허설 런북 | 레포 루트 또는 `ops/` |
| 운영 기록 | `release.log` | 배포 결과 기록(성공/실패) | 서버에 생성(커밋 금지) |
| 기록 템플릿 | `release.log.template` | `release.log` 작성용 템플릿 | 레포(커밋 가능) |

---

## 2. docker-compose.prod.yml 운영 원칙

### 2.1 공통
- 이미지 태그 고정: `backend:<TAG>`, `frontend:<TAG>`, `db:<TAG>`
- `restart: unless-stopped`
- `healthcheck`는 **db/backend/nginx(또는 frontend)**에 필수
- 운영에서는 `.env.sample`을 사용하지 않습니다(샘플은 **키 목록** 확인용).

### 2.2 DB (Postgres + pgvector)
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  timeout: 5s
  retries: 6
```

### 2.3 Backend (FastAPI)
코드 수정 없이 사용할 수 있는 확인 경로로 `openapi.json`을 사용합니다.
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://localhost:8000/openapi.json >/dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 6
```

### 2.4 Nginx/Frontend (정적 Nginx)
정적 서빙 확인:
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://localhost/ >/dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 6
```

프록시 확인(선택, 운영 권장):
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- http://localhost/api/openapi.json >/dev/null 2>&1"]
  interval: 10s
  timeout: 5s
  retries: 6
```

---

## 3. 시크릿/환경변수 정책(.env.prod)

### 3.1 원칙
- 레포에는 `.env.sample`만 유지합니다(키 이름만).
- 서버에는 `.env.prod`를 생성해 **실제 값을 주입**합니다.
- `docker compose ... config`는 환경변수 값이 노출될 수 있으니 공유/로그 업로드 시 반드시 마스킹합니다.

### 3.2 최소 키 목록
`.env.sample`의 키를 기준으로 `.env.prod`에 동일 키가 모두 있어야 합니다.  
(예: `OPENAI_API_KEY`, `JWT_SECRET_KEY`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `LANGCHAIN_API_KEY` 등)

---

## 4. 배포 절차(표준)

### 4.1 Preflight (실패를 먼저 만들기)
1) compose 유효성:
```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml config
```
2) 컨테이너 기동 전 필수 키 확인(값 출력 금지 원칙)
- 가능하면 `preflight_all.ps1`(Windows) 같은 스크립트로 자동화합니다.

### 4.2 Build → Up
```bash
# <TAG>는 사전에 결정(8절 참고)
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 4.3 Health 확인
```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200
```

### 4.4 Smoke Test (5분 컷)
- Frontend:
```bash
curl -fsS http://localhost/ >/dev/null
```
- Backend 프록시:
```bash
curl -fsS http://localhost/api/openapi.json >/dev/null
```

> 인증이 필요한 RAG 엔드포인트를 반드시 포함해야 하는 경우, 별도 토큰/권한 정책이 확정된 뒤에 추가합니다.

### 4.5 기록(release.log)
- 배포 성공/실패 결과와 <TAG>, 시간, 핵심 로그 위치를 `release.log`에 남깁니다.
- 템플릿은 `release.log.template`을 복사해 사용합니다.

---

## 5. 롤백(최소 전략)

원칙: **직전 태그(<TAG_PREV>)로 재기동**이 기본입니다.
```bash
# docker-compose.prod.yml에서 이미지 태그를 <TAG_PREV>로 맞춘 뒤
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```
DB 마이그레이션 롤백이 필요한 경우는 별도 절차로 관리합니다(데이터 손실 위험).

---

## 6. Preflight 체크리스트(운영 게이트)

- [ ] `docker compose --env-file .env.prod -f docker-compose.prod.yml config`가 성공한다
- [ ] `.env.prod`에 `.env.sample`의 모든 키가 존재한다(값은 출력하지 않는다)
- [ ] `<TAG>` 규칙이 결정되어 있고, `release.log`에 기록할 준비가 되어 있다
- [ ] `docker compose ... ps`에서 컨테이너가 정상 상태로 올라온다
- [ ] healthcheck가 db/backend/nginx에서 정상(healthy) 상태로 전환된다

---

## 7. Smoke Test 체크리스트(운영 직후)

- [ ] `GET /` (정적 서빙)
- [ ] `GET /api/openapi.json` (프록시)
- [ ] `docker compose ... logs`에서 치명 오류(반복 재시작/크래시)가 없다
- [ ] 실패 시 `release.log`에 “Minimum Failure Record”를 남긴다

---

## 8. 태그 규칙(<TAG>)

- `<TAG>`는 운영 배포 단위를 나타냅니다.
- 표준 형식(택1):
  - 날짜형: `YYYY.MM.DD`
  - 커밋형: `git short SHA`
- 예시:
  - `backend:2026.01.14`
  - `frontend:2026.01.14`

---

## 9. 운영 1회 리허설(가능할 때)

리허설이 가능해지면 아래 순서로 1회 수행하고, 결과를 `release.log`에 남깁니다.

1) `.env.prod` 준비(서버에만 존재)
2) `<TAG>` 결정
3) `config` → `up` → `ps`
4) healthcheck 확인
5) smoke test
6) 성공/실패 기록

---

## 10. 게이트(사내 CI 또는 대체 게이트)

현재 단계(사내망/로컬 개발)에서는 **수동 게이트 + release.log 증빙**을 운영 표준으로 둡니다.  
향후 가능해지면 GitHub Actions 또는 사내 CI로 lint/test 게이트를 추가합니다(옵션).

---

## 11. 변경 이력

- 날짜 / 변경 요약 / 작성자 / 승인자

























# 사내망 Docker Compose 운영 배포 런북 (deploy.md)

## 0. 목적과 범위
이 문서는 **사내망 내부 서버**에서 이 서비스를 **Docker Compose로 실행**할 때, “한 번의 리허설 배포”를 **재현 가능**하게 만드는 것을 목표로 합니다.

- 이 문서는 **GitLab/EC2/SSH 기반 배포**를 전제로 하지 않습니다.
- 배포 방식은 **서버 로컬 Build**(서버에서 docker build/compose build 수행)입니다.
- 문서/스크립트는 “운영 배포 패키지(ops package)”로 취급합니다.

---

## 1. 고정 규칙(바꾸면 문서도 같이 바꿈)
다음 3가지는 운영 표준으로 **고정**합니다.

1) 프록시 smoke/health 경로: **`/api/openapi.json`**  
2) 운영 env: **`.env.prod` 파일 방식**(서버 로컬 파일)  
3) 배포 흐름: **서버 로컬 Build**(레지스트리 Pull 전제 아님)

---

## 2. 운영 배포 패키지 구성(레포 산출물)
아래 파일들이 “운영 배포 패키지”입니다. 경로는 레포 구조에 맞게 유지하세요.

- `ops/deploy.md` : 이 문서
- `ops/release.log.template` : 운영 기록 템플릿(성공/실패)
- `ops/release.log` : 실제 운영 기록(템플릿 복사해서 생성)
- `docker-compose.prod.yml` : 운영용 Compose
- `scripts/preflight_all.ps1` : Windows PowerShell 단일 진입점(Preflight)
- `.env.sample` : **키 목록 표준(값 없음)**  
- `.env.prod` : **운영 실값(서버에만 존재, 커밋 금지)**

---

## 3. 시크릿/환경변수 정책(.env.prod / .env.sample)
### 3.1 단일 규칙
- 운영 실값은 **`.env.prod`**로만 관리합니다(서버 로컬 파일).
- `.env.prod`는 **커밋 금지**, 접근 권한 최소화.
- `.env.sample`은 **키 목록 표준**입니다(값 없음/더미만, 커밋 가능).
- 운영 경로에서 `backend/app/core/.env.sample` 같은 **하위 샘플 파일은 참조하지 않습니다**(혼선 방지).

### 3.2 서버 권한(권장)
Linux 서버라면 권한을 최소화합니다.

```bash
chmod 600 .env.prod
```

Windows 서버라면 파일 ACL로 접근 권한을 제한합니다(팀 정책 우선).

---

## 4. 이미지 태그(TAG) 규칙과 기록

### 4.1 TAG 규칙(운영 표준)

TAG는 “운영 배포 단위”입니다. 아래 중 하나로 고정합니다.

* 날짜형: `YYYY.MM.DD` (예: `2026.01.14`)
* 커밋형: `git short SHA` (예: `a1b2c3d`)

운영 예시:

* `backend:2026.01.14`
* `frontend:2026.01.14`

### 4.2 기록 원칙

* 배포를 시작하기 전에 TAG를 결정합니다.
* 배포 후 **`ops/release.log`**에 TAG와 결과를 남깁니다.
* 롤백은 **직전 TAG로 재기동**을 최소 전략으로 합니다.

---

## 5. Preflight(배포 전 강제 점검)

### 5.1 목적

배포 전 “필수 파일/키/compose 유효성”을 강제해서, 실패를 가능한 앞쪽에서 터뜨립니다.

### 5.2 PowerShell 단일 진입점(권장)

Windows 기준:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/preflight_all.ps1 -EnvFile .env.prod
```

* `.env.prod`가 없으면 **의도적으로 실패**해야 정상입니다.
* Preflight는 최소 다음을 확인해야 합니다:

  * `.env.prod` 존재
  * `.env.sample` 기준의 **필수 키 존재 여부(값 출력 금지)**
  * `docker-compose.prod.yml` config 유효성
  * TAG 존재 여부(정책에 따라)

### 5.3 docker compose config 출력 주의(민감값 노출)

`docker compose ... config`는 **환경변수 값이 출력될 수 있습니다.**

* 문서 검증 목적이면 출력 억제를 권장합니다.
* PowerShell 예시:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml config | Out-Null
if ($LASTEXITCODE -ne 0) { throw "compose config failed" }
```

---

## 6. 운영 1회 리허설 런북(가장 중요한 절차)

리허설은 “실서버에 올리기 전, 동일한 명령으로 1회 통과”하는 것을 의미합니다.

### 6.1 준비

1. 서버에 `.env.prod` 생성(값 입력, 커밋 금지)
2. TAG 결정(4절 규칙)
3. `ops/release.log.template` → `ops/release.log`로 복사

### 6.2 배포(서버 로컬 Build)

아래는 예시입니다. 레포 경로/서비스명은 실제 파일과 맞추세요.

```powershell
# 1) preflight
powershell -ExecutionPolicy Bypass -File scripts/preflight_all.ps1 -EnvFile .env.prod

# 2) build + up
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build

# 3) 상태 확인
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

### 6.3 Healthcheck 확인

healthcheck는 compose 파일에 정의되어 있어야 합니다. (예: db/ backend / nginx)

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=200
```

### 6.4 Smoke Test(3~5분)

최소 smoke는 아래 2개만 통과해도 “서비스가 살아있다”로 판단합니다.

```bash
# 1) 프론트 정적 서빙
curl -fsS http://localhost/ >/dev/null

# 2) 프록시를 통해 backend OpenAPI 확인 (고정 규칙)
curl -fsS http://localhost/api/openapi.json >/dev/null
```

선택(권장, 인증 필요):

```bash
curl -fsS -H "Authorization: Bearer ***" http://localhost/api/v1/collections >/dev/null
```

### 6.5 운영 기록 남기기(release.log)

* 성공/실패 모두 `ops/release.log`에 기록합니다.
* 형식은 `ops/release.log.template`를 그대로 사용합니다.
* 실패 시에는 최소 기록 포맷(Minimum Failure Record)을 반드시 채웁니다.

---

## 7. 롤백(최소 전략)

롤백은 “직전 TAG로 재기동”을 기본으로 합니다.

1. 문제 TAG 확인(현재 배포 TAG)
2. 직전 TAG를 결정
3. compose에서 이미지 태그를 직전 TAG로 맞춘 뒤 재기동

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml down
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d
```

데이터 마이그레이션이 포함되면, 롤백 가능/불가 여부를 release.log에 명확히 남깁니다.

---

## 8. 장애 대응(현장에서 바로 쓰는 순서)

1. `docker compose ps`로 상태 확인(Exited/Restarting)
2. `docker compose logs --tail=200`로 **첫 에러** 확인
3. DB healthcheck 실패 → DB부터 해결
4. 프록시(/api/openapi.json) 실패 → nginx 라우팅/백엔드 기동 여부 분리
5. 인증 실패(401/403) → 토큰/권한/환경변수(JWT_SECRET_KEY 등) 확인(값 노출 금지)

---

## 9. 부록: 운영 배포 패키지 체크리스트(리허설 기준)

* [ ] `.env.prod` 존재(서버에만) / 커밋 금지
* [ ] `.env.sample`은 키 목록만 포함(값 없음)
* [ ] Preflight 통과(`scripts/preflight_all.ps1`)
* [ ] `docker compose up -d --build` 성공
* [ ] `curl http://localhost/api/openapi.json` 성공
* [ ] `ops/release.log`에 TAG/결과 기록
* [ ] 실패 시 Minimum Failure Record 기록

---

## 10. 부록: 이후 개선(백로그)

리허설 1회 통과 이후에 진행해도 됩니다.

* CI/게이트 도입(GitHub Actions 또는 사내 게이트)
* JWT 기본 시크릿 fail-fast 강제(APP_ENV=prod)
* MCP tool allowlist/RBAC/timeout/audit 정책 고정
* LLM 호출 안정성(timeout/retry/backoff) 표준화

```

---

## 선택지
1) **위 “휴머나이즈드 v2”를 `ops/deploy.md`로 단일화**하고, `deploy_humanized.md`는 삭제(가장 실용적)  
2) `deploy_humanized.md`를 계속 유지하되, **미리보기 `...`가 섞이지 않은 “원본 파일”로 다시 생성**한 뒤 비교(관리 비용 증가)  
3) 문서 톤은 v2로 단일화하고, 별도 파일 대신 **“문서 작성 규칙(스타일 가이드)” 1페이지**만 남김(장기 유지에 유리)

원하시면, 지금 업로드된 `deploy_humanized.md`에서 보이는 `발...flight` 같은 **잘림이 어디서 생겼는지(복사/인코딩/에디터 설정)**를 재발 방지 관점에서 짧게 정리해 드리겠습니다.
```
