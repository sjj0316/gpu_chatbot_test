import { kyClient } from "@/shared/api/ky-client";
import {
  modelApiKeyUpdateSchema,
  modelApiKeyReadWithSecretSchema,
  type ModelApiKeyUpdate,
  type ModelApiKeyReadWithSecret,
} from "../model";

export const updateModelKey = async (
  keyId: number,
  payload: ModelApiKeyUpdate
): Promise<ModelApiKeyReadWithSecret> => {
  const body = modelApiKeyUpdateSchema.parse(payload);
  const res = await kyClient.patch(`api-keys/${keyId}`, { json: body }).json();
  return modelApiKeyReadWithSecretSchema.parse(res);
};
