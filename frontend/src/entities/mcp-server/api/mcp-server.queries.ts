export const mcpServerQueries = {
  all: ["mcp-servers"] as const,
  list: (q: string | null | undefined, offset: number, limit: number) =>
    [...mcpServerQueries.all, "list", { q: q ?? null, offset, limit }] as const,
  detail: (id: number) => [...mcpServerQueries.all, "detail", id] as const,
};
