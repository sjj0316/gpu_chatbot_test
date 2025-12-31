import { queryOptions } from "@tanstack/react-query";
import { getModelKeys } from "./get-model-keys";
import { getDetailModelKey } from "./get-detail-model-key";
import type { AiModelKeysListParams } from "../model";

export const modelKeyQueries = {
  all: () => ["ai-model-keys"] as const,

  list: (params?: AiModelKeysListParams) =>
    queryOptions({
      queryKey: [...modelKeyQueries.all(), "list", params] as const,
      queryFn: () => getModelKeys(params),
      staleTime: 5 * 60 * 1000,
    }),

  detail: (id: number, opts?: { reveal_secret?: boolean }) =>
    queryOptions({
      queryKey: [...modelKeyQueries.all(), "detail", id, opts] as const,
      queryFn: () => getDetailModelKey(id, opts),
      staleTime: 5 * 60 * 1000,
    }),
};
