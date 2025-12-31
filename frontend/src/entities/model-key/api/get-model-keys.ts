import { kyClient } from "@/shared/api/ky-client";
import {
  aiModelKeysListParamsSchema,
  aiModelKeysListResponseSchema,
  type AiModelKeysListParams,
  type AiModelKeysListResponse,
} from "../model";

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
