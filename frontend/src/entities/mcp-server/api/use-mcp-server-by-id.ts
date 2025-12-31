import { useQuery } from "@tanstack/react-query";
import { getDetailMcpServer } from "./get-detail-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

export const useMcpServerById = (id: number | null | undefined) => {
  return useQuery({
    queryKey: id ? mcpServerQueries.detail(id) : ["mcp-servers", "detail", "disabled"],
    queryFn: () => getDetailMcpServer(id as number),
    enabled: !!id,
    staleTime: 30_000,
  });
};
