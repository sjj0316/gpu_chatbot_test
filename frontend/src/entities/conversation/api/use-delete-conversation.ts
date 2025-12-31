import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteConversation } from "./delete-conversation";
import { conversationQueries } from "./conversation.queries";

export function useDeleteConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: number) => deleteConversation(conversationId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.all });
    },
  });
}
