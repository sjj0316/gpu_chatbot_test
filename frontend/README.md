# BD 챗봇

## 목차

- [1. 설명](#설명)
- [2. 설치](#설치)
- [3. 실행](#실행)

## 설명

- 주요 라이브러리
  - react
  - tanstack query (+ ky)
  - zustand
  - shadcn/ui (+ tailwind v4)

- 디렉터리 구조 : FSD (Feature Sliced Design) 구조로 설계되어 있습니다.
  - src/
    - app/
    - pages/
    - widgets/
    - features/
    - entities/
    - shared/

## 설치

- 프로젝트 세팅에 맞는 패키지 매니저를 사용합니다 (e.g. npm, pnpm, yarn ...)

```bash
npm install
# or
pnpm install
# or
yarn install
```

## 실행

```bash
npm run dev
pnpm run dev
yarn dev
```

## 환경 변수

- 프론트에서 백엔드 API 엔드포인트를 변경하려면 `frontend/.env` 파일을 만들고 아래 값을 설정하세요:

```env
VITE_API_BASE_URL=http://localhost:8000
```

이 값을 변경하면 `frontend/src/shared/api/ky-client.ts`에서 사용하는 기본 API 베이스 URL이 변경됩니다.

## Docker

프론트는 도커로도 실행할 수 있습니다. 루트 `docker-compose.yml`을 사용하면 개발용 백엔드와 함께 프론트를 실행할 수 있습니다.

```powershell
docker compose up --build
```

