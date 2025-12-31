import { useQuery } from "@tanstack/react-query";

import { conversationQueries } from "./conversation.queries";
import { getConversations, type GetConversationsParams } from "./get-conversations";

export function useConversations(params?: GetConversationsParams) {
  return useQuery({
    queryKey: conversationQueries.list(params),
    queryFn: () => getConversations(params),
    staleTime: 10_000,
  });
}
