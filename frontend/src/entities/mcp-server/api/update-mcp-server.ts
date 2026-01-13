import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead, MCPServerUpdate } from "../model";

/**
 * Why: MCP 서버 정보를 부분 수정합니다.
 *
 * Contract:
 * - id는 1 이상의 정수여야 합니다.
 *
 * @returns 수정된 MCP 서버 상세.
 */
export const updateMcpServer = async (id: number, body: MCPServerUpdate) => {
  const res = await kyClient.patch(`mcp-servers/${id}`, { json: body }).json<MCPServerRead>();
  return res;
};
