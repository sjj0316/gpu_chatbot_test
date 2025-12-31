# ⬇ 기존과 동일
FROM node:22 AS build
WORKDIR /app

# ⚠️ 회사망 전용 dev 꼼수: Node TLS 검증 끄기 (프론트 빌드 스텝에만 적용)
#   - 회사 프록시/사설 인증서 때문에 npm 레지스트리 TLS가 깨지는 걸 우회
ENV NODE_TLS_REJECT_UNAUTHORIZED=0

# (선택) npm strict-ssl도 같이 꺼두면 혹시 모를 문제 예방
RUN npm config set strict-ssl false

# corepack 실행 (여기서도 위 ENV를 물고 감)
RUN corepack enable

# 루트 기준이라 frontend/ 경로 붙여서 복사
COPY frontend/package.json frontend/pnpm-lock.yaml* ./

# pnpm 설치 (여기서 npmjs.org에 TLS로 붙음 → 위 ENV로 검증 회피)
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
