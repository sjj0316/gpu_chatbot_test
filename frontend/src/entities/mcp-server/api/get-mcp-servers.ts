import { kyClient } from "@/shared/api/ky-client";
import type { MCPServersListResponse, MCPServersListParams } from "../model";

/**
 * Why: 접근 가능한 MCP 서버 목록을 조회합니다.
 *
 * Contract:
 * - q/offset/limit을 쿼리로 전달합니다.
 *
 * @returns MCP 서버 목록.
 */
export const getMcpServers = async (params: MCPServersListParams = {}) => {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (typeof params.offset === "number") search.set("offset", String(params.offset));
  if (typeof params.limit === "number") search.set("limit", String(params.limit));
  const qs = search.toString();
  const url = `mcp-servers${qs ? `?${qs}` : ""}`;
  const res = await kyClient.get(url).json<MCPServersListResponse>();
  return res;
};
