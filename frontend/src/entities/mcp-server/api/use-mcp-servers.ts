import { useQuery } from "@tanstack/react-query";

import { getMcpServers } from "./get-mcp-servers";
import { mcpServerQueries } from "./mcp-server.queries";

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
