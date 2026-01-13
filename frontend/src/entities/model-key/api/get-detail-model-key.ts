import { kyClient } from "@/shared/api/ky-client";
import {
  getModelKeyParamsSchema,
  modelApiKeyReadWithSecretSchema,
  type GetModelKeyParams,
  type ModelApiKeyReadWithSecret,
} from "../model";

/**
 * Why: 특정 모델 키의 상세 정보를 조회합니다.
 *
 * Contract:
 * - reveal_secret 파라미터는 스키마로 검증됩니다.
 * - 응답은 비밀키 포함 스키마로 파싱됩니다.
 *
 * @returns 모델 키 상세 정보.
 */
export const getDetailModelKey = async (
  keyId: number,
  params?: GetModelKeyParams
): Promise<ModelApiKeyReadWithSecret> => {
  const parsed = getModelKeyParamsSchema.parse(params ?? {});
  const res = await kyClient
    .get(`api-keys/${keyId}`, {
      searchParams: parsed as Record<string, string | number | boolean>,
    })
    .json();
  return modelApiKeyReadWithSecretSchema.parse(res);
};
