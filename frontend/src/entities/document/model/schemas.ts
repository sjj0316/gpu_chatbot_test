import { z } from "zod";

export const chunkItemSchema = z.object({
  id: z.string(),
  content: z.string(),
  metadata: z.record(z.any()),
  source: z.string().nullable().optional(),
});

export const documentChunkSchema = z.object({
  id: z.string(),
  content: z.string(),
  metadata: z.record(z.any()),
  collection_id: z.string(),
});

export const documentFileSchema = z.object({
  file_id: z.string(),
  source: z.string(),
  chunk_count: z.number().int(),
  chunks: z.array(chunkItemSchema),
});

export const paginatedChunkResponseSchema = z.object({
  items: z.array(chunkItemSchema),
  chunk_total: z.number().int(),
  file_total: z.number().int(),
});

export const paginatedDocumentResponseSchema = z.object({
  items: z.array(documentFileSchema),
  chunk_total: z.number().int(),
  file_total: z.number().int(),
});

export const documentReadSchema = z.object({
  file_id: z.string(),
  file_name: z.string(),
  chunk_count: z.number().int(),
});

export const documentUploadRequestSchema = z.object({
  files: z.any(),
  metadatas_json: z.string().optional(),
  chunk_size: z.number().int().optional(),
  chunk_overlap: z.number().int().optional(),
  model_api_key_id: z.number().int().optional(),
});

export const documentUploadResponseSchema = z.object({
  success: z.boolean(),
  message: z.string(),
  added_chunk_ids: z.array(z.string()),
  warnings: z.array(z.string()).optional(),
});

export const documentDeleteRequestSchema = z.object({
  file_ids: z.array(z.string()).optional(),
  document_ids: z.array(z.string()).optional(),
});

export const documentViewTypeSchema = z.enum(["document", "chunk"]);

export const documentsListParamsSchema = z.object({
  limit: z.number().int().min(1).max(100).optional(),
  offset: z.number().int().min(0).optional(),
  view: documentViewTypeSchema.optional(),
});

export const documentSearchTypeSchema = z.enum(["semantic", "keyword", "hybrid"]);

export const documentsSearchRequestSchema = z.object({
  query: z.string(),
  limit: z.number().int().optional(),
  filter: z.record(z.any()).optional(),
  search_type: documentSearchTypeSchema.optional(),
  module_api_key_id: z.number().int().optional(),
});

export const documentsSearchResponseItemSchema = z.object({
  id: z.string(),
  page_content: z.string(),
  metadata: z.record(z.any()),
  score: z.number().nullable().optional(),
});

export const documentsSearchResponseSchema = z.array(documentsSearchResponseItemSchema);
