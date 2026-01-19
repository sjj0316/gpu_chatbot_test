## 테스트 개요

이 폴더는 FastAPI 백엔드의 라우터/서비스 단위 테스트와 스모크 테스트를 포함합니다.
DB 및 인증 의존성은 대부분 테스트에서 오버라이드하여 외부 의존성을 최소화합니다.

## 테스트 실행 방법

가장 기본 실행:

```bash
pytest backend/tests
```

특정 파일만 실행:

```bash
pytest backend/tests/test_user_service.py
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

- `conftest.py`: 테스트 전역 설정(이벤트 루프, 경로 설정).
- `test_auth_router.py`: 로그인/비밀번호 변경 관련 라우터 테스트.
- `test_conversations_router.py`: 대화 생성/목록/히스토리/삭제/스트리밍 라우터 테스트.
- `test_mcp_server_router.py`: MCP 서버 생성/목록/수정/삭제 라우터 테스트.
- `test_mcp_server_service.py`: MCP 서버 서비스의 권한/공개 여부 처리 테스트.
- `test_model_api_keys_router.py`: 모델 API 키 조회/생성/수정/삭제 및 권한 테스트.
- `test_rag_router.py`: 컬렉션 생성/목록/문서 업로드 라우터 테스트.
- `test_smoke.py`: 루트/오픈API/기본 엔드포인트 응답 스모크 테스트.
- `test_user_router.py`: 사용자 등록/조회 라우터 테스트.
- `test_user_service.py`: 사용자 생성 서비스 로직(중복/기본 역할) 테스트.
- `test_wiki_router.py`: 위키 조회/업서트 라우터 테스트.

## 참고 사항

- 라우터 테스트는 `httpx.AsyncClient`와 `ASGITransport`를 사용합니다.
- DB 접근은 실제 연결 대신 의존성 오버라이드로 대체합니다.
- 인증 의존성(`get_current_user`)도 테스트 내에서 오버라이드하여 권한 분기를 검증합니다.
- 일부 테스트 데이터에 한글 문자열이 포함되어 있으며, 인코딩 환경에 따라 깨질 수 있습니다.
