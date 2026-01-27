# BD 챗봇 프런트엔드

React + Vite 기반의 클라이언트 애플리케이션입니다. 상태 관리와 서버 상태 동기화를 위해 Zustand, TanStack Query(Ky)를 사용하며 UI는 shadcn/ui(Tailwind v4)로 구성됩니다.

## 1. 주요 스택 및 구조

- React, Vite
- TanStack Query + Ky(HTTP)
- Zustand
- shadcn/ui + Tailwind CSS v4
- 구조: FSD(Feature Sliced Design)
  - `src/app/`, `src/pages/`, `src/widgets/`, `src/features/`, `src/entities/`, `src/shared/`

### 폴더 역할(요약)
- `src/app/`: 앱 엔트리/라우터/프로바이더
- `src/pages/`: 라우트 단위 화면
- `src/widgets/`: 페이지를 구성하는 큰 UI 블록
- `src/features/`: 기능 단위 UI/로직(예: 로그인 폼)
- `src/entities/`: 도메인 모델 + API 훅
- `src/shared/`: 공용 컴포넌트, 유틸, API 클라이언트

## 2. 설치

선호하는 패키지 매니저를 사용하세요.

```bash
pnpm install
# 또는
npm install
yarn install
```

## 3. 개발 서버 실행

```bash
pnpm run dev
# 또는
npm run dev
yarn dev
```

## 4. 환경변수

API 베이스 URL 설정 예시(`frontend/.env`):

```env
VITE_API_BASE_URL=http://localhost:8000
```

값을 변경하면 `src/shared/api/ky-client.ts`에서 사용하는 기본 API URL이 함께 바뀝니다.

### 인증 토큰 처리
- `localStorage`에 `authToken`, `refreshToken` 저장
- 만료 감지 시 `/api/v1/auth/refresh`로 1회 재발급 시도
- 재발급 실패 시 토큰 제거 후 `/login`으로 이동

## 5. Docker 실행

루트의 `docker-compose.yml`을 사용하면 프런트엔드가 Nginx(80 포트)로 함께 기동됩니다.

```powershell
docker compose up --build
```

## 6. 라우팅(경로별 설명)

라우팅 설정 파일: `src/app/router/app-router.tsx`

### 공개 경로
- `/login`: 로그인 화면 (`LoginPage`)
- `/register`: 회원가입 화면 (`RegisterPage`)

### 보호된 경로(로그인 필요)
모든 보호 경로는 `ProtectedRoute`로 감싸져 있으며, 인증 실패 시 `/login`으로 이동합니다.

- `/` : 홈 (기능/가이드 카드 요약)
- `/about` : 서비스 소개
- `/chat` : 채팅 UI (대화/스트리밍)
- `/collections` : 컬렉션 관리
- `/documents` : 문서 업로드/관리
- `/search` : 문서 검색(semantic/keyword/hybrid)
- `/model-keys` : 모델 API 키 관리
- `/mcp-servers` : MCP 서버 관리
- `/change-password` : 비밀번호 변경
- `/profile` : 프로필 편집 + 비밀번호 변경
- `/guide` : 사용 가이드 보기/편집(위키)

### 예외 경로
- `*` : NotFound 페이지

## 7. API 연결 방식

- 공통 클라이언트: `src/shared/api/ky-client.ts`
  - `prefixUrl = {VITE_API_BASE_URL}/api/v1`
  - 401 응답 시 토큰 갱신 후 1회 재시도
- 각 도메인 API 훅은 `src/entities/*/api`에 위치

## 8. 추가 문서

- 전체 프로젝트 개요: `../README.md`
- 백엔드 설정: `../backend/README.md`
