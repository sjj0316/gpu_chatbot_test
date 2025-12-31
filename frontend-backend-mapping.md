# Frontend ↔ Backend API Mapping

이 문서는 프론트엔드(`frontend/`)에서 호출하는 API와 백엔드(`backend/`)에 구현된 라우터를 비교하여 누락/불일치 항목과 권장 조치를 정리합니다.

## 요약
- 프론트엔드에서 사용되는 대부분의 엔드포인트가 백엔드에 구현되어 있음.
- 백엔드는 모델/서비스/라우터/알렘빅 마이그레이션 등 핵심 아키텍처가 구성되어 있음.
- 부족한 점: 테스트 부족, 일부 엔드포인트의 권한/응답 형태 불일치 가능성, 그리고 문서화/엔드포인트 스펙 표준화 필요.

---

## 백엔드 엔드포인트 (app/routers 기준)
- `POST /api/v1/auth/login` -> 로그인
- `POST /api/v1/auth/refresh` -> 토큰 리프레시
- `GET  /api/v1/auth/me` -> 현재 사용자 정보

- `POST /api/v1/users` -> 유저 등록

- Conversation 관련
  - `POST /api/v1/conversations` -> 대화 생성
  - `GET  /api/v1/conversations` -> 대화 목록
  - `GET  /api/v1/conversations/{conversation_id}/histories` -> 히스토리 조회
  - `DELETE /api/v1/conversations/{conversation_id}` -> 대화 삭제
  - `POST /api/v1/conversations/{conversation_id}/invoke` -> 동기적 챗 호출
  - `POST /api/v1/conversations/{conversation_id}/stream` -> SSE 스트리밍 채팅

- RAG / Collections / Documents
  - `POST   /api/v1/collections/` -> 컬렉션 생성
  - `GET    /api/v1/collections/` -> 컬렉션 목록
  - `GET    /api/v1/collections/{collection_id}` -> 컬렉션 상세
  - `PATCH  /api/v1/collections/{collection_id}` -> 컬렉션 수정
  - `DELETE /api/v1/collections/{collection_id}` -> 컬렉션 삭제

  - `POST   /api/v1/collections/{collection_id}/documents` -> 문서 업로드 (multipart/form-data)
  - `GET    /api/v1/collections/{collection_id}/documents` -> 문서/청크 목록 (query: view=document|chunk)
  - `DELETE /api/v1/collections/{collection_id}/documents` -> 문서 전체 삭제 (body: file_ids/document_ids)
  - `DELETE /api/v1/collections/{collection_id}/documents/{target_id}` -> 단일 문서 삭제 (query: delete_by=file_id|document_id)
  - `POST   /api/v1/collections/{collection_id}/documents/search` -> 문서 검색

- API Key 관리
  - `POST   /api/v1/api-keys` -> API 키 생성
  - `GET    /api/v1/api-keys` -> API 키 목록
  - `GET    /api/v1/api-keys/{key_id}` -> 단일 키 조회 (reveal_secret query)
  - `PATCH  /api/v1/api-keys/{key_id}` -> 키 수정
  - `DELETE /api/v1/api-keys/{key_id}` -> 키 삭제

- MCP Servers
  - `POST   /api/v1/mcp-servers` -> MCP 서버 생성
  - `GET    /api/v1/mcp-servers` -> MCP 서버 목록
  - `GET    /api/v1/mcp-servers/{server_id}` -> MCP 서버 상세
  - `PATCH  /api/v1/mcp-servers/{server_id}` -> MCP 서버 수정
  - `DELETE /api/v1/mcp-servers/{server_id}` -> MCP 서버 삭제


## 프론트엔드에서 호출하는 엔드포인트 (주요 파일 기준)
- Auth / User
  - `POST /api/v1/auth/login` (프론트: `frontend/src/entities/user/api/index.ts`)
  - `POST /api/v1/auth/refresh` (프론트: `frontend/src/shared/api/ky-client.ts`, `frontend/src/entities/user/api/index.ts`)
  - `GET  /api/v1/auth/me` (프론트: `frontend/src/entities/user/api/index.ts`)

- Collections / Documents (프론트: `frontend/src/entities/collection/api/*`, `frontend/src/entities/document/api/*`)
  - `POST   /api/v1/collections` -> `createCollection`
  - `GET    /api/v1/collections` -> `getCollections` / `useCollections`
  - `POST   /api/v1/collections/{id}/documents` -> `createDocument` (FormData)
  - `GET    /api/v1/collections/{id}/documents` -> `getDocuments`
  - `DELETE /api/v1/collections/{id}/documents` -> `deleteDocuments`
  - `DELETE /api/v1/collections/{id}/documents/{targetId}` -> `deleteDocumentById`
  - `POST   /api/v1/collections/{id}/documents/search` -> `searchDocuments`

- Conversations / Chat (프론트: `frontend/src/entities/conversation/api/*`)
  - `POST   /api/v1/conversations` -> `createConversation`
  - `GET    /api/v1/conversations` -> `getConversations`
  - `GET    /api/v1/conversations/{id}/histories` -> `getHistories`
  - `DELETE /api/v1/conversations/{id}` -> `deleteConversation`
  - `POST   /api/v1/conversations/{id}/invoke` -> `invokeChat`
  - `POST   /api/v1/conversations/{id}/stream` -> `streamChat` (SSE)

- API Keys (프론트: `frontend/src/entities/model-key/api/*`)
  - `POST   /api/v1/api-keys` -> `createModelKey`
  - `GET    /api/v1/api-keys` -> `getModelKeys`
  - `GET    /api/v1/api-keys/{id}` -> `getDetailModelKey`
  - `PATCH  /api/v1/api-keys/{id}` -> `updateModelKey`
  - `DELETE /api/v1/api-keys/{id}` -> `deleteModelKey`

- MCP Servers (프론트: `frontend/src/entities/mcp-server/api/*`)
  - `POST   /api/v1/mcp-servers` -> `createMcpServer`
  - `GET    /api/v1/mcp-servers` -> `getMcpServers`
  - `GET    /api/v1/mcp-servers/{id}` -> `getDetailMcpServer`
  - `PATCH  /api/v1/mcp-servers/{id}` -> `updateMcpServer`
  - `DELETE /api/v1/mcp-servers/{id}` -> `deleteMcpServer`


## 매핑 요약
- 거의 모든 프론트 호출이 백엔드 라우터에 대응됨.
- 핵심 매핑(인증, 컬렉션/문서, 대화, 스트리밍, API 키, MCP 서버)은 일치.


## 누락 / 불일치 항목
- 경로 형식: 프론트는 `kyClient`에 `prefixUrl: ${API_BASE_URL}/api/v1`을 사용하므로 경로는 상대경로(`collections`, `conversations`)로 호출되어 백엔드의 `/api/v1` 프리픽스와 잘 매칭됨.
- 테스트: 프론트는 풍부한 UI-레벨 훅을 제공하지만 백엔드에는 자동화된 테스트가 거의 없음(테스트 폴더에 `__init__.py`만 존재). 이는 통합 시 회귀 위험을 높임.
- 권한·응답 스펙 불일치 가능성: 일부 엔드포인트(예: `api-keys/{id}` reveal_secret, chunk/document view 등)는 프론트에서 특정 query/headers/body를 기대함. 실제 응답 스키마가 완벽히 일치하는지 자동 검증 필요.
- 엔드포인트 사용되지 않음: 백엔드에 구현되어 있으나 프론트에서 찾지 못한 엔드포인트(예: `POST /api/v1/users` 등록 API)는 프론트에서 직접 호출하는 위치가 없음(회원가입 UI가 없는 것으로 보임).


## 권장 액션
1. 엔드포인트 스펙 문서화 (OpenAPI/Swagger 보완 또는 별도 API 스펙 문서). 우선순위: 높.
2. 간단한 통합 스모크 테스트 추가: 로그인, get /, create collection, create conversation, stream start(부분) — 우선순위: 높.
3. 핵심 엔드포인트에 대한 pytest 기반 단위/통합 테스트 추가(2~4개) — 우선순위: 중.
4. `POST /api/v1/users` 사용 여부 확인: 필요시 프론트에 회원가입 UI 추가 또는 백엔드 제거/비공개 처리 — 우선순위: 낮.
5. CI 파이프라인에 lint + tests 실행 추가(가능하면 도커·uv 환경에서 마이그레이션 적용 테스트 포함) — 우선순위: 중.


---

작성자: 자동 매핑 스크립트 (요약)
생성일: 2025-12-29
