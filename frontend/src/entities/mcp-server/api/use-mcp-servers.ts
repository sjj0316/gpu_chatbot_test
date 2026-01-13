import { useQuery } from "@tanstack/react-query";

import { getMcpServers } from "./get-mcp-servers";
import { mcpServerQueries } from "./mcp-server.queries";

/**
 * Why: MCP 서버 목록을 페이지네이션 기반으로 조회합니다.
 *
 * Contract:
 * - page/pageSize로 offset/limit을 계산합니다.
 * - 쿼리 키에 검색어와 페이지 정보를 포함합니다.
 *
 * @returns React Query 결과 객체.
 */
export const useMcpServers = ({
  q,
  page = 1,
  pageSize = 20,
}: {
  q?: string | null;
  page?: number;
  pageSize?: number;
}) => {
  const offset = Math.max(0, (page - 1) * pageSize);
  const limit = pageSize;
  return useQuery({
    queryKey: mcpServerQueries.list(q ?? null, offset, limit),
    queryFn: () => getMcpServers({ q: q ?? undefined, offset, limit }),
    staleTime: 30_000,
  });
};
