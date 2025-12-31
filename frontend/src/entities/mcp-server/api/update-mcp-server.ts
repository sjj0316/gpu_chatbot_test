import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead, MCPServerUpdate } from "../model";

export const updateMcpServer = async (id: number, body: MCPServerUpdate) => {
  const res = await kyClient.patch(`mcp-servers/${id}`, { json: body }).json<MCPServerRead>();
  return res;
};
