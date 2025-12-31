import ky from "ky";

// const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:3000";
const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// JWT 토큰 만료 확인 함수
const isTokenExpired = (token: string): boolean => {  
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentTime = Math.floor(Date.now() / 1000);
    return payload.exp < currentTime;
  } catch (error) {
    return true;
  }
};

// 토큰 리프레시 함수
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
    // 리프레시 토큰도 만료된 경우
    localStorage.removeItem("authToken");
    localStorage.removeItem("refreshToken");
    window.location.href = "/login";
    return null;
  }
};

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
