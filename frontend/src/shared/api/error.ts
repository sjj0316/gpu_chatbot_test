import { HTTPError } from "ky";

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
