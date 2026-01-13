import { kyClient } from "@/shared/api/ky-client";
import {
  modelApiKeyCreateSchema,
  modelApiKeyReadWithSecretSchema,
  type ModelApiKeyCreate,
  type ModelApiKeyReadWithSecret,
} from "../model";

/**
 * Why: 새 모델 API 키를 등록해 이후 호출에 재사용합니다.
 *
 * Contract:
 * - payload는 스키마로 검증됩니다.
 * - 응답은 비밀키 포함 스키마로 파싱됩니다.
 *
 * @returns 등록된 모델 키(비밀키 포함).
 */
export const createModelKey = async (
  payload: ModelApiKeyCreate
): Promise<ModelApiKeyReadWithSecret> => {
  const body = modelApiKeyCreateSchema.parse(payload);
  const res = await kyClient.post("api-keys", { json: body }).json();
  return modelApiKeyReadWithSecretSchema.parse(res);
};
