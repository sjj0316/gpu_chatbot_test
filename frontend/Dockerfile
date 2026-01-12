# 프로덕션 빌드용
FROM node:24.12.0 AS build
WORKDIR /app

# corepack 실행
RUN corepack enable

# 루트 기준이라 frontend/ 경로 붙여서 복사
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# pnpm 설치
RUN pnpm install --frozen-lockfile

# 실제 소스 복사
COPY frontend/ .

# 빌드
RUN pnpm run build

# ---- nginx 스테이지 ----
FROM nginx:alpine

COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
