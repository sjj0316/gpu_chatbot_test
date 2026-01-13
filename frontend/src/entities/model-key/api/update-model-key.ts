import { kyClient } from "@/shared/api/ky-client";
import {
  modelApiKeyUpdateSchema,
  modelApiKeyReadWithSecretSchema,
  type ModelApiKeyUpdate,
  type ModelApiKeyReadWithSecret,
} from "../model";

/**
 * Why: 모델 키의 메타데이터/활성 상태를 갱신합니다.
 *
 * Contract:
 * - payload는 스키마로 검증됩니다.
 * - 응답은 비밀키 포함 스키마로 파싱됩니다.
 *
 * @returns 수정된 모델 키(비밀키 포함).
 */
export const updateModelKey = async (
  keyId: number,
  payload: ModelApiKeyUpdate
): Promise<ModelApiKeyReadWithSecret> => {
  const body = modelApiKeyUpdateSchema.parse(payload);
  const res = await kyClient.patch(`api-keys/${keyId}`, { json: body }).json();
  return modelApiKeyReadWithSecretSchema.parse(res);
};
