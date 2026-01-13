import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead } from "../model";

/**
 * Why: MCP 서버 상세 정보를 조회합니다.
 *
 * Contract:
 * - id는 1 이상의 정수여야 합니다.
 *
 * @returns MCP 서버 상세.
 */
export const getDetailMcpServer = async (id: number) => {
  const res = await kyClient.get(`mcp-servers/${id}`).json<MCPServerRead>();
  return res;
};
