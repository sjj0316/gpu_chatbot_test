import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead, MCPServerCreate } from "../model";

export const createMcpServer = async (body: MCPServerCreate) => {
  const res = await kyClient.post(`mcp-servers`, { json: body }).json<MCPServerRead>();
  return res;
};
