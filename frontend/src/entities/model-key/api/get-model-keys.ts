import { kyClient } from "@/shared/api/ky-client";
import {
  aiModelKeysListParamsSchema,
  aiModelKeysListResponseSchema,
  type AiModelKeysListParams,
  type AiModelKeysListResponse,
} from "../model";

/**
 * Why: 사용자/공개 모델 키 목록을 조건에 맞게 조회합니다.
 *
 * Contract:
 * - 요청 파라미터는 스키마로 검증됩니다.
 * - 응답은 목록 스키마로 파싱됩니다.
 *
 * @returns 모델 키 목록과 메타데이터.
 */
export const getModelKeys = async (
  params?: AiModelKeysListParams
): Promise<AiModelKeysListResponse> => {
  const parsed = aiModelKeysListParamsSchema.parse(params ?? {});
  const res = await kyClient
    .get("api-keys", {
      searchParams: parsed as Record<string, string | number | boolean>,
    })
    .json();
  return aiModelKeysListResponseSchema.parse(res);
};
