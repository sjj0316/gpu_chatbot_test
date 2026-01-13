import { kyClient } from "@/shared/api/ky-client";

/**
 * Why: MCP 서버 연결 정보를 삭제합니다.
 *
 * Contract:
 * - id는 1 이상의 정수여야 합니다.
 *
 * @returns 삭제 성공 여부.
 */
export const deleteMcpServer = async (id: number) => {
  await kyClient.delete(`mcp-servers/${id}`);
  return true;
};
