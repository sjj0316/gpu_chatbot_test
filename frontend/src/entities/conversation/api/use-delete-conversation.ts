import { useMutation, useQueryClient } from "@tanstack/react-query";
import { deleteConversation } from "./delete-conversation";
import { conversationQueries } from "./conversation.queries";

/**
 * Why: 대화 삭제 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 목록 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export function useDeleteConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: number) => deleteConversation(conversationId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.all });
    },
  });
}
