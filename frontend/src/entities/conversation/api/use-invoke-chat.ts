import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invokeChat } from "./invoke-chat";
import { conversationQueries } from "./conversation.queries";
import type { ChatRequest } from "../model";

/**
 * Why: 단일 응답 채팅 mutation을 제공해 히스토리를 갱신합니다.
 *
 * Contract:
 * - 성공 시 히스토리 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export function useInvokeChat(conversationId: number) {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ChatRequest) => invokeChat(conversationId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: conversationQueries.histories(conversationId) });
    },
  });
}
