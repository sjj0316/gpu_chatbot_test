import { kyClient } from "@/shared/api/ky-client";
import type { MCPServerRead, MCPServerCreate } from "../model";

/**
 * Why: MCP 서버 연결 정보를 등록합니다.
 *
 * Contract:
 * - body는 서버 생성 스키마를 따라야 합니다.
 *
 * @returns 생성된 MCP 서버 상세.
 */
export const createMcpServer = async (body: MCPServerCreate) => {
  const res = await kyClient.post(`mcp-servers`, { json: body }).json<MCPServerRead>();
  return res;
};
