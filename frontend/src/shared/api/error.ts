import { HTTPError } from "ky";

/**
 * Why: API 실패 원인을 사용자 친화적인 메시지로 변환합니다.
 *
 * Contract:
 * - HTTPError의 detail을 우선 사용하고, 없으면 상태 코드/문구를 반환합니다.
 *
 * @returns 표시 가능한 오류 메시지.
 */
export const getApiErrorMessage = async (
  error: unknown,
  fallback = "알 수 없는 오류가 발생했습니다."
): Promise<string> => {
  if (error instanceof HTTPError) {
    try {
      const data = await error.response.json();
      if (data && typeof data.detail === "string") {
        return data.detail;
      }
    } catch {
      // Ignore JSON parsing errors.
    }
    return `${error.response.status} ${error.response.statusText}`.trim();
  }

  if (error instanceof Error && error.message) {
    return error.message;
  }

  return fallback;
};
