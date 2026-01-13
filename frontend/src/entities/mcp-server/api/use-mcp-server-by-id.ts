import { useQuery } from "@tanstack/react-query";
import { getDetailMcpServer } from "./get-detail-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

/**
 * Why: MCP 서버 상세 정보를 조회합니다.
 *
 * Contract:
 * - id가 없으면 조회를 비활성화합니다.
 *
 * @returns React Query 결과 객체.
 */
export const useMcpServerById = (id: number | null | undefined) => {
  return useQuery({
    queryKey: id ? mcpServerQueries.detail(id) : ["mcp-servers", "detail", "disabled"],
    queryFn: () => getDetailMcpServer(id as number),
    enabled: !!id,
    staleTime: 30_000,
  });
};
