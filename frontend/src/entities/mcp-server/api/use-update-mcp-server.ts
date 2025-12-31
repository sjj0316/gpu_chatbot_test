import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { updateMcpServer } from "./update-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

export const useUpdateMcpServer = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof updateMcpServer>[1] }) =>
      updateMcpServer(id, body),
    onSuccess: (_, { id }) => {
      qc.invalidateQueries({ queryKey: mcpServerQueries.detail(id) });
      qc.invalidateQueries({ queryKey: mcpServerQueries.all });
      toast.success("성공", { description: "MCP 서버가 수정되었습니다." });
    },
    onError: (err) => {
      const message = err instanceof Error ? err.message : "MCP 서버 수정에 실패했습니다.";
      toast.error("오류", { description: message });
    },
  });
};
