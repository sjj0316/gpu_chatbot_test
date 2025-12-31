import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createConversation } from "./create-conversation";
import { conversationQueries } from "./conversation.queries";
import type { ConversationCreate } from "../model";

export function useCreateConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ConversationCreate) => createConversation(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.all });
    },
  });
}
