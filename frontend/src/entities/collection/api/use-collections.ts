import { useQuery } from "@tanstack/react-query";

import { collectionQueries } from "./collection.queries";
import type { CollectionsListParams } from "../model";

/**
 * Why: 컬렉션 목록을 React Query로 조회합니다.
 *
 * Contract:
 * - params 변경 시 queryKey가 갱신됩니다.
 *
 * @returns React Query 결과 객체.
 */
export const useCollections = (params?: CollectionsListParams) => {
  return useQuery(collectionQueries.list(params));
};
