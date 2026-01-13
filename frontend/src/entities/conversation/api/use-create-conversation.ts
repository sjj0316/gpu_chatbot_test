import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createConversation } from "./create-conversation";
import { conversationQueries } from "./conversation.queries";
import type { ConversationCreate } from "../model";

/**
 * Why: 대화 생성 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 목록 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export function useCreateConversation() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ConversationCreate) => createConversation(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.all });
    },
  });
}
