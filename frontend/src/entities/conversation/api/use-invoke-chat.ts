import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invokeChat } from "./invoke-chat";
import { conversationQueries } from "./conversation.queries";
import type { ChatRequest } from "../model";

export function useInvokeChat(conversationId: number) {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ChatRequest) => invokeChat(conversationId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.histories(conversationId) });
    },
  });
}
