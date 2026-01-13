import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { deleteMcpServer } from "./delete-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

/**
 * Why: MCP 서버 삭제 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 목록 쿼리를 무효화합니다.
 * - 실패 시 오류 메시지를 사용자에게 노출합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useDeleteMcpServer = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteMcpServer,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mcpServerQueries.all });
      toast.success("성공", { description: "MCP 서버가 삭제되었습니다." });
    },
    onError: (err) => {
      const message =
        err instanceof Error ? err.message : "MCP 서버 삭제에 실패했습니다.";
      toast.error("오류", { description: message });
    },
  });
};
