import { kyClient } from "@/shared/api/ky-client";
import {
  modelApiKeyCreateSchema,
  modelApiKeyReadWithSecretSchema,
  type ModelApiKeyCreate,
  type ModelApiKeyReadWithSecret,
} from "../model";

export const createModelKey = async (
  payload: ModelApiKeyCreate
): Promise<ModelApiKeyReadWithSecret> => {
  const body = modelApiKeyCreateSchema.parse(payload);
  const res = await kyClient.post("api-keys", { json: body }).json();
  return modelApiKeyReadWithSecretSchema.parse(res);
};
