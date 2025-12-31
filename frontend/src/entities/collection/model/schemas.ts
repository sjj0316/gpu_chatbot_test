import { z } from "zod";

export const collectionSchema = z.object({
  collection_id: z.string().uuid(),
  table_id: z.string(),
  name: z.string(),
  description: z.string().nullable().optional(),
  is_public: z.boolean(),
  embedding_id: z.number().int().nullable().optional(),
  embedding_dimension: z.number().int().nullable().optional(),
  embedding_model: z.string().nullable().optional(),
  owner_id: z.number().int(),
  document_count: z.number().int(),
  chunk_count: z.number().int(),
});

export const createCollectionSchema = z.object({
  name: z.string().min(1, "이름은 필수입니다."),
  description: z.string().nullable().optional(),
  is_public: z.boolean().optional(),
  model_api_key_id: z.number().int().nullable().optional(),
});

export const updateCollectionSchema = z.object({
  name: z.string().min(1, "이름은 필수입니다.").optional(),
  description: z.string().nullable().optional(),
  is_public: z.boolean().optional(),
});

export const collectionsListResponseSchema = z.object({
  total_count: z.number().int(),
  items: z.array(collectionSchema),
});

export const collectionsListParamsSchema = z.object({
  limit: z.number().int().min(1).max(100).optional(),
  offset: z.number().int().min(0).optional(),
});
