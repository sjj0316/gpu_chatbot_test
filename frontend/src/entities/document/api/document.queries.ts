import { queryOptions } from "@tanstack/react-query";
import { getDocuments } from "./get-documents";
import type { DocumentsListParams } from "../model";

export const documentQueries = {
  all: (collectionId: string) => ["collections", collectionId, "documents"] as const,

  list: (collectionId: string, params?: DocumentsListParams) =>
    queryOptions({
      queryKey: [
        ...documentQueries.all(collectionId),
        "list",
        params?.view ?? "document",
        params?.limit ?? 10,
        params?.offset ?? 0,
      ] as const,
      queryFn: () => getDocuments(collectionId, params),
      staleTime: 5 * 60 * 1000,
    }),
};
