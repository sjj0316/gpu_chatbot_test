import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { searchDocuments } from "./search-documents";
import { type DocumentSearchRequest } from "../model";

/**
 * Why: 문서 검색 mutation을 제공해 사용자 요청에 응답합니다.
 *
 * Contract:
 * - 요청 실패 시 오류 토스트를 노출합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useSearchDocument = () => {
  return useMutation({
    mutationFn: ({
      collectionId,
      request,
    }: {
      collectionId: string;
      request: DocumentSearchRequest;
    }) => searchDocuments(collectionId, request),
    onError: (error) => {
      toast.error("오류", { description: "검색에 실패했습니다." });
      console.error("Search error:", error);
    },
  });
};
