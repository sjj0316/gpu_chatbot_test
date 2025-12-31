import { useMutation } from "@tanstack/react-query";
import { toast } from "sonner";

import { searchDocuments } from "./search-documents";
import { type DocumentSearchRequest } from "../model";

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
