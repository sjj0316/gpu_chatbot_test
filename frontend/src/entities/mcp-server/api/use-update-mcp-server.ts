import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { updateMcpServer } from "./update-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

/**
 * Why: MCP 서버 수정 mutation을 제공해 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 상세/목록 쿼리를 무효화합니다.
 * - 실패 시 오류 메시지를 사용자에게 노출합니다.
 *
 * @returns React Query mutation 객체.
 */
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
      const message =
        err instanceof Error ? err.message : "MCP 서버 수정에 실패했습니다.";
      toast.error("오류", { description: message });
    },
  });
};
