import { useQuery } from "@tanstack/react-query";
import { conversationQueries } from "./conversation.queries";
import { getHistories } from "./get-histories";

export function useHistories(conversationId: number, enabled = true) {
  return useQuery({
    queryKey: conversationQueries.histories(conversationId),
    queryFn: () => getHistories(conversationId),
    enabled,
    staleTime: 0,
  });
}
