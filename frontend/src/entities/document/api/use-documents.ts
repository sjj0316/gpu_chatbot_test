import { useQuery } from "@tanstack/react-query";

import { documentQueries } from "./document.queries";
import { type DocumentsListParams } from "../model";

/**
 * Why: 컬렉션 문서 목록을 React Query로 조회합니다.
 *
 * Contract:
 * - collectionId가 없으면 조회를 비활성화합니다.
 *
 * @returns React Query 결과 객체.
 */
export const useDocuments = (collectionId: string, params?: DocumentsListParams) => {
  return useQuery({ ...documentQueries.list(collectionId, params), enabled: !!collectionId });
};
