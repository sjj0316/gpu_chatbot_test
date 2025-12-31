import { kyClient } from "@/shared/api/ky-client";
import {
  getModelKeyParamsSchema,
  modelApiKeyReadWithSecretSchema,
  type GetModelKeyParams,
  type ModelApiKeyReadWithSecret,
} from "../model";

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
