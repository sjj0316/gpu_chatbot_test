import { z } from "zod";
import {
  transportSchema,
  mcpServerConfigSchema,
  mcpServerBaseSchema,
  mcpServerCreateSchema,
  mcpServerUpdateSchema,
  mcpServerReadSchema,
  mcpServersListResponseSchema,
  mcpServersListParamsSchema,
  mcpServerRuntimeSchema,
  mcpToolInfoSchema,
} from "./schemas";

export type TransportLiteral = z.infer<typeof transportSchema>;
export type MCPServerConfig = z.infer<typeof mcpServerConfigSchema>;
export type MCPToolInfo = z.infer<typeof mcpToolInfoSchema>;
export type MCPServerRuntime = z.infer<typeof mcpServerRuntimeSchema>;

export type MCPServerBase = z.infer<typeof mcpServerBaseSchema>;
export type MCPServerCreate = z.infer<typeof mcpServerCreateSchema>;
export type MCPServerUpdate = z.infer<typeof mcpServerUpdateSchema>;
export type MCPServerRead = z.infer<typeof mcpServerReadSchema>;

export type MCPServersListResponse = z.infer<typeof mcpServersListResponseSchema>;
export type MCPServersListParams = z.infer<typeof mcpServersListParamsSchema>;
