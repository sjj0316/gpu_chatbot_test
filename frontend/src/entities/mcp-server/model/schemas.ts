import { z } from "zod";

const transportInputSchema = z
  .string()
  .min(1)
  .transform((v) => v.trim().toLowerCase().replace(/-/g, "_"));
export const transportSchema = transportInputSchema.pipe(z.enum(["http", "streamable_http"]));

const mcpServerConfigObject = z
  .object({
    transport: transportSchema,
    url: z.string().url().nullable().optional(),
  })
  .passthrough();

export const mcpServerConfigSchema = mcpServerConfigObject.superRefine((val, ctx) => {
  if ((val.transport === "http" || val.transport === "streamable_http") && !val.url) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, path: ["url"], message: "HTTP 계열은 URL이 필수" });
  }
});

export const mcpToolInfoSchema = z.object({
  name: z.string(),
  description: z.string().nullable().optional(),
  input_schema: z.record(z.any()).nullable().optional(),
});

export const mcpServerRuntimeSchema = z.object({
  reachable: z.boolean(),
  error: z.string().nullable().optional(),
  tools: z.array(mcpToolInfoSchema).default([]),
});

export const mcpServerBaseSchema = z.object({
  name: z.string().min(1).max(100),
  description: z.string().max(1000).nullable().optional().default(null),
  config: mcpServerConfigSchema,
  is_public: z.boolean().default(false),
});

export const mcpServerCreateSchema = mcpServerBaseSchema;

export const mcpServerUpdateSchema = z.object({
  name: z.string().min(1).max(100).nullable().optional(),
  description: z.string().max(1000).nullable().optional(),
  config: mcpServerConfigSchema.optional(),
  is_public: z.boolean().optional(),
});

export const mcpServerReadSchema = z.object({
  id: z.number().int(),
  name: z.string(),
  description: z.string().nullable().optional(),
  config: mcpServerConfigSchema,
  is_public: z.boolean(),
  owner_id: z.number().int(),
  runtime: mcpServerRuntimeSchema.nullable().optional().default(null),
});

export const mcpServersListResponseSchema = z.array(mcpServerReadSchema);

export const mcpServersListParamsSchema = z.object({
  q: z.string().optional(),
  offset: z.number().int().min(0).optional(),
  limit: z.number().int().min(1).max(200).optional(),
});
