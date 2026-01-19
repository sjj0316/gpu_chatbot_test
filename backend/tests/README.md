## 테스트 개요

이 폴더는 FastAPI 백엔드의 단위/라우터 테스트와 통합(E2E) 테스트를 포함합니다.
단위/라우터 테스트는 의존성을 오버라이드해 빠르고 안정적으로 로직을 검증하고,
통합 테스트는 실제 DB 및 환경 설정을 사용해 시스템 전체 흐름을 확인합니다.

## 테스트 실행 방법

가장 기본 실행:

```bash
pytest backend/tests
```

특정 파일만 실행:

```bash
pytest backend/tests/test_user_service.py
```

통합 테스트만 실행:

```bash
pytest backend/tests/integration
```

실패 지점 디버깅을 위한 출력 증가:

```bash
pytest -vv backend/tests
```

## 자주 발생하는 오류 및 해결

### `pytest-cov` 관련 옵션 오류

다음과 같은 오류가 발생하면 `pytest-cov` 플러그인이 설치되지 않은 상태입니다.

```
pytest: error: unrecognized arguments: --cov=app --cov-report=term-missing --cov-fail-under=80
```

해결 방법:

```bash
uv sync --dev
```

또는

```bash
python -m pip install pytest-cov
```

## 테스트 항목(파일별)

### 단위/라우터 테스트 (`backend/tests`)

- `conftest.py`: 테스트 전역 설정(이벤트 루프, 경로 설정).
- `test_auth_router.py`: 로그인/비밀번호 변경 라우터 테스트.
- `test_conversations_router.py`: 대화 생성/목록/히스토리/삭제/스트리밍 라우터 테스트.
- `test_mcp_server_router.py`: MCP 서버 생성/목록/수정/삭제 라우터 테스트.
- `test_mcp_server_service.py`: MCP 서버 서비스 권한/공개 여부 처리 테스트.
- `test_model_api_keys_router.py`: 모델 API 키 조회/생성/수정/삭제 및 권한 테스트.
- `test_rag_router.py`: 컬렉션 생성/목록/문서 업로드 라우터 테스트.
- `test_smoke.py`: 루트/오픈API/기본 엔드포인트 응답 스모크 테스트.
- `test_user_router.py`: 사용자 등록/조회 라우터 테스트.
- `test_user_service.py`: 사용자 생성 서비스 로직(중복/기본 역할) 테스트.
- `test_wiki_router.py`: 위키 조회/업서트 라우터 테스트.

### 통합 테스트 (`backend/tests/integration`)

- `conftest.py`: 통합 테스트용 공통 클라이언트/DB 보정/인증 헬퍼.
- `test_authz.py`: 권한 시나리오(사용자/관리자) 검증.
- `test_migrations_and_extensions.py`: 마이그레이션 및 확장(pg_trgm/vector) 상태 확인.
- `test_model_keys_with_env.py`: 환경변수 기반 API 키 등록/조회/정리.
- `test_model_key_errors.py`: 잘못된 API 키 입력 에러 처리 검증.
- `test_rag_e2e.py`: RAG 컬렉션 생성/업로드/검색/정리 E2E 흐름.
- `test_wiki_e2e.py`: 위키 CRUD E2E 흐름.

## 참고 사항

- 라우터 테스트는 `httpx.AsyncClient`와 `ASGITransport`를 사용합니다.
- 단위/라우터 테스트는 DB 접근을 의존성 오버라이드로 대체합니다.
- 통합 테스트는 `DATABASE_URL` 등 환경 변수와 실제 DB 준비가 필요합니다.
- 인증 의존성(`get_current_user`)도 테스트 내에서 오버라이드하여 권한 분기를 검증합니다.
- 일부 테스트 데이터에 한글 문자열이 포함되어 있으며, 인코딩 환경에 따라 깨질 수 있습니다.
