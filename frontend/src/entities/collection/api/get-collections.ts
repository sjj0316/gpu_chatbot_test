import { kyClient } from "@/shared/api/ky-client";
import {
  collectionsListResponseSchema,
  type CollectionsListParams,
  type CollectionsListResponse,
} from "../model";

/**
 * Why: 컬렉션 목록을 필터/페이지네이션으로 조회합니다.
 *
 * Contract:
 * - params는 목록 스키마에 따라 검증됩니다.
 *
 * @returns 컬렉션 목록 응답.
 */
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
