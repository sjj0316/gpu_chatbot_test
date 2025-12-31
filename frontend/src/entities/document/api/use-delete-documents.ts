import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { documentQueries } from "./document.queries";
import { deleteDocuments } from "./delete-documents";
import { type DocumentDeleteRequest } from "../model";

export const useDeleteDocuments = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ collectionId, data }: { collectionId: string; data: DocumentDeleteRequest }) =>
      deleteDocuments(collectionId, data),
    onSuccess: (_, { collectionId }) => {
      queryClient.invalidateQueries({ queryKey: documentQueries.all(collectionId) });
      toast.success("성공", { description: "문서가 삭제되었습니다." });
    },
    onError: (error) => {
      toast.error("오류", { description: "문서 삭제에 실패했습니다" });
    },
  });
};
