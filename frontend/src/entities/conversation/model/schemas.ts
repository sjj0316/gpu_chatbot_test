import { z } from "zod";

export const conversationCreateSchema = z.object({
  title: z.string().nullable().optional(),
  default_model_key_id: z.number().int().nullable().optional(),
  default_params: z.record(z.any()).nullable().optional(),
  mcp_server_ids: z.array(z.number().int()).nullable().optional(),
});

export const conversationReadSchema = z.object({
  id: z.number().int(),
  title: z.string().nullable().optional(),
});
export const conversationListItemSchema = conversationReadSchema;

// 재귀 JSON 스키마
export type Json = string | number | boolean | null | { [key: string]: Json } | Json[];

export const jsonSchema: z.ZodType<Json> = z.lazy(() =>
  z.union([
    z.string(),
    z.number(),
    z.boolean(),
    z.null(),
    z.array(jsonSchema),
    z.record(jsonSchema),
  ])
);

export const historyItemSchema = z.object({
  id: z.number().int(),
  role: z.enum(["system", "user", "assistant", "tool"]),
  content: z.string().nullable().optional(),
  timestamp: z.string(),

  input_tokens: z.number().int().nullable().optional(),
  output_tokens: z.number().int().nullable().optional(),
  cost: z.number().nullable().optional(),
  latency_ms: z.number().int().nullable().optional(),

  tool_name: z.string().nullable().optional(),
  tool_call_id: z.string().nullable().optional(),
  tool_input: jsonSchema.nullable().optional(),
  tool_output: jsonSchema.nullable().optional(),
  error: z.string().nullable().optional(),
});

export const chatRequestSchema = z.object({
  conversation_id: z.number().int().nullable().optional(),
  message: z.string().min(1),
  model_key_id: z.number().int().nullable().optional(),
  params: z.record(z.any()).nullable().optional(),
  system_prompt: z.string().nullable().optional(),
  mcp_server_ids: z.array(z.number().int()).nullable().optional(),
});

export const chatChunkSchema = z.object({
  type: z.enum(["token", "update", "done", "error"]),
  data: z.record(z.any()),
});

export const chatResponseSchema = z.object({
  conversation_id: z.number().int(),
  message_id: z.number().int(),
  content: z.string(),
});
