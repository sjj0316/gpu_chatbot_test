# BD 챗봇 프런트엔드

React + Vite 기반의 클라이언트 애플리케이션입니다. 상태 관리와 서버 상태 동기화를 위해 Zustand, TanStack Query(Ky)를 사용하며 UI는 shadcn/ui(Tailwind v4)로 구성됩니다.

## 1. 주요 스택 및 구조

- React, Vite
- TanStack Query + Ky(HTTP)
- Zustand
- shadcn/ui + Tailwind CSS v4
- 구조: FSD(Feature Sliced Design)
  - `src/app/`, `src/pages/`, `src/widgets/`, `src/features/`, `src/entities/`, `src/shared/`

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

## 5. Docker 실행

루트의 `docker-compose.yml`을 사용하면 프런트엔드가 Nginx(80 포트)로 함께 기동됩니다.

```powershell
docker compose up --build
```

## 6. 추가 문서

- 전체 프로젝트 개요: `../README.md`
- 백엔드 설정: `../backend/README.md`
