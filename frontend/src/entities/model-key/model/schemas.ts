import { z } from "zod";

export const modelApiKeyBaseSchema = z.object({
  alias: z.string().max(50).nullable().optional(),
  provider_code: z.string().min(1).max(32),
  model: z.string().min(1).max(100),
  endpoint_url: z.string().max(255).nullable().optional(),
  purpose_code: z.string().min(1).max(32),
  is_public: z.boolean().default(false),
  is_active: z.boolean().default(true),
  extra: z.record(z.any()).nullable().optional(),
});

export const modelApiKeyCreateSchema = modelApiKeyBaseSchema.extend({
  api_key: z.string().min(1),
});

export const modelApiKeyUpdateSchema = z.object({
  alias: z.string().nullable().optional(),
  provider_code: z.string().nullable().optional(),
  model: z.string().nullable().optional(),
  endpoint_url: z.string().nullable().optional(),
  purpose_code: z.string().nullable().optional(),
  is_public: z.boolean().nullable().optional(),
  is_active: z.boolean().nullable().optional(),
  extra: z.record(z.any()).nullable().optional(),
  api_key: z.string().nullable().optional(),
});

export const modelApiKeyReadSchema = z.object({
  id: z.number(),
  alias: z.string().nullable().optional(),
  provider_id: z.number(),
  provider_code: z.string().nullable().optional(),
  model: z.string(),
  endpoint_url: z.string().nullable().optional(),
  purpose_id: z.number(),
  purpose_code: z.string().nullable().optional(),
  is_public: z.boolean(),
  is_active: z.boolean(),
  extra: z.record(z.any()).nullable().optional(),
  owner_id: z.number(),
  owner_nickname: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string().nullable().optional(),
  api_key_masked: z.string().nullable().optional(),
});

export const modelApiKeyReadWithSecretSchema = modelApiKeyReadSchema.extend({
  api_key: z.string().nullable().optional(),
});

export const aiModelKeysListResponseSchema = z.array(modelApiKeyReadSchema);

export const aiModelKeysListParamsSchema = z.object({
  include_public: z.boolean().optional(),
  provider_code: z.string().optional(),
  purpose_code: z.string().optional(),
  is_active: z.boolean().optional(),
  limit: z.number().int().min(1).max(200).optional(),
  offset: z.number().int().min(0).optional(),
  owner_id: z.number().int().optional(),
});

export const getModelKeyParamsSchema = z.object({
  reveal_secret: z.boolean().optional(),
});
