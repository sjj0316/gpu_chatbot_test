import ky from "ky";

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Why: JWT 만료 여부를 확인해 재발급이 필요한지 판단합니다.
 *
 * Contract:
 * - 디코딩 실패 시 만료로 간주합니다.
 */
const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};

/**
 * Why: 만료된 액세스 토큰을 갱신하고 저장소를 동기화합니다.
 *
 * Contract:
 * - refreshToken이 없으면 null을 반환합니다.
 * - 재발급 실패 시 로컬 토큰을 제거하고 로그인으로 이동합니다.
 */
const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = localStorage.getItem("refreshToken");
  if (!refreshToken) {
    return null;
  }

  try {
    const response = await ky
      .post(`${API_BASE_URL}/api/v1/auth/refresh`, {
        json: { refresh_token: refreshToken },
        timeout: 30000,
      })
      .json<{ access_token: string; refresh_token: string }>();

    localStorage.setItem("authToken", response.access_token);
    localStorage.setItem("refreshToken", response.refresh_token);
    return response.access_token;
  } catch (error) {
    localStorage.removeItem("authToken");
    localStorage.removeItem("refreshToken");
    window.location.href = "/login";
    return null;
  }
};

/**
 * Why: API 요청에 인증/재시도 로직을 적용한 공통 HTTP 클라이언트입니다.
 *
 * Contract:
 * - Authorization 헤더는 localStorage의 토큰을 사용합니다.
 * - 401 응답 시 1회 토큰 갱신 후 재시도합니다.
 */
export const kyClient = ky.create({
  prefixUrl: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
  hooks: {
    beforeRequest: [
      async (request) => {
        let token = localStorage.getItem("authToken");

        if (token) {
          // 토큰 만료 확인
          if (isTokenExpired(token)) {
            // 토큰 리프레시 시도
            const newToken = await refreshAccessToken();
            token = newToken;
          }

          if (token) {
            request.headers.set("Authorization", `Bearer ${token}`);
          }
        }
      },
    ],
    afterResponse: [
      async (request, options, response) => {
        if (response.status === 401) {
          // 401 응답시 토큰 리프레시 시도
          const newToken = await refreshAccessToken();
          if (newToken) {
            // 새 토큰으로 원래 요청 재시도
            const newRequest = new Request(request);
            newRequest.headers.set("Authorization", `Bearer ${newToken}`);
            return ky(newRequest);
          }
        }
        return response;
      },
    ],
  },
});
