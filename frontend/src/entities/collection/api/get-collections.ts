import { kyClient } from "@/shared/api/ky-client";
import {
  collectionsListResponseSchema,
  type CollectionsListParams,
  type CollectionsListResponse,
} from "../model";

export const getCollections = async (
  params?: CollectionsListParams
): Promise<CollectionsListResponse> => {
  const res = await kyClient
    .get("collections", {
      searchParams: params as Record<string, string | number | boolean>,
    })
    .json();
  return collectionsListResponseSchema.parse(res);
};
