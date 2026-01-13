import { useQuery } from "@tanstack/react-query";

import { conversationQueries } from "./conversation.queries";
import { getConversations, type GetConversationsParams } from "./get-conversations";

/**
 * Why: 대화 목록을 React Query로 조회합니다.
 *
 * Contract:
 * - params가 변경되면 queryKey가 갱신됩니다.
 *
 * @returns React Query 결과 객체.
 */
export function useConversations(params?: GetConversationsParams) {
  return useQuery({
    queryKey: conversationQueries.list(params),
    queryFn: () => getConversations(params),
    staleTime: 10_000,
  });
}
