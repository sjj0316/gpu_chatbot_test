import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { documentQueries } from "./document.queries";
import { deleteDocumentById } from "./delete-document-by-id";

/**
 * Why: 단일 문서/파일 삭제 mutation을 제공해 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 컬렉션 문서 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useDeleteDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      collectionId,
      targetId,
      deleteBy,
    }: {
      collectionId: string;
      targetId: string;
      deleteBy: "file_id" | "document_id";
    }) => deleteDocumentById(collectionId, targetId, deleteBy),
    onSuccess: (_, { collectionId }) => {
      queryClient.invalidateQueries({ queryKey: documentQueries.all(collectionId) });
      toast.success("성공", { description: "문서가 삭제되었습니다." });
    },
    onError: () => {
      toast.error("오류", { description: "문서 삭제에 실패했습니다." });
    },
  });
};
