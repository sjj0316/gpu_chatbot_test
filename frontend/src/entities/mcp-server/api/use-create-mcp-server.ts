import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { createMcpServer } from "./create-mcp-server";
import { mcpServerQueries } from "./mcp-server.queries";

export const useCreateMcpServer = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createMcpServer,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: mcpServerQueries.all });
      toast.success("성공", { description: "MCP 서버가 생성되었습니다." });
    },
    onError: (err) => {
      const message = err instanceof Error ? err.message : "MCP 서버 생성에 실패했습니다.";
      toast.error("오류", { description: message });
    },
  });
};
