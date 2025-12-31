import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead } from "../model";

export const getDetailMcpServer = async (id: number) => {
  const res = await kyClient.get(`mcp-servers/${id}`).json<MCPServerRead>();
  return res;
};
