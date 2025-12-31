import { z } from "zod";
import {
  modelApiKeyBaseSchema,
  modelApiKeyCreateSchema,
  modelApiKeyUpdateSchema,
  modelApiKeyReadSchema,
  modelApiKeyReadWithSecretSchema,
  aiModelKeysListResponseSchema,
  getModelKeyParamsSchema,
} from "./schemas";

export type ModelApiKeyBase = z.infer<typeof modelApiKeyBaseSchema>;
export type ModelApiKeyCreate = z.infer<typeof modelApiKeyCreateSchema>;
export type ModelApiKeyUpdate = z.infer<typeof modelApiKeyUpdateSchema>;
export type ModelApiKeyRead = z.infer<typeof modelApiKeyReadSchema>;
export type ModelApiKeyReadWithSecret = z.infer<typeof modelApiKeyReadWithSecretSchema>;

export type AiModelKeysListResponse = z.infer<typeof aiModelKeysListResponseSchema>;
export type AiModelKeysListParams = {
  include_public?: boolean;
  provider_code?: string;
  purpose_code?: string;
  is_active?: boolean;
  limit?: number;
  offset?: number;
  owner_id?: number;
};

export type GetModelKeyParams = z.infer<typeof getModelKeyParamsSchema>;
