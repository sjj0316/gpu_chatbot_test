export const conversationQueries = {
  all: ["conversations"] as const,
  list: (params?: { limit?: number; offset?: number }) =>
    [...conversationQueries.all, "list", params ?? {}] as const,
  histories: (conversationId: number) =>
    [...conversationQueries.all, conversationId, "histories"] as const,
  detail: (conversationId: number) =>
    [...conversationQueries.all, conversationId, "detail"] as const,
};
