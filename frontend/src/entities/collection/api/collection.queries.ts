import { queryOptions } from "@tanstack/react-query";
import { getCollections } from "./get-collections";
import { getDetailCollection } from "./get-detail-collection";
import type { CollectionsListParams } from "../model";

export const collectionQueries = {
  all: () => ["collections"] as const,

  list: (params?: CollectionsListParams) =>
    queryOptions({
      queryKey: [...collectionQueries.all(), "list", params] as const,
      queryFn: () => getCollections(params),
      staleTime: 5 * 60 * 1000,
    }),

  detail: (id: string) =>
    queryOptions({
      queryKey: [...collectionQueries.all(), "detail", id] as const,
      queryFn: () => getDetailCollection(id),
      staleTime: 5 * 60 * 1000,
    }),
};
