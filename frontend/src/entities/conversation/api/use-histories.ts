import { useQuery } from "@tanstack/react-query";
import { conversationQueries } from "./conversation.queries";
import { getHistories } from "./get-histories";

/**
 * Why: 대화 히스토리를 React Query로 조회합니다.
 *
 * Contract:
 * - enabled가 false면 요청을 중단합니다.
 *
 * @returns React Query 결과 객체.
 */
export function useHistories(conversationId: number, enabled = true) {
  return useQuery({
    queryKey: conversationQueries.histories(conversationId),
    queryFn: () => getHistories(conversationId),
    enabled,
    staleTime: 0,
  });
}
