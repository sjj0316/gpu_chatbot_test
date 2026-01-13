import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { documentQueries } from "./document.queries";
import { createDocument } from "./create-document";
import { type DocumentUploadRequest } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

/**
 * Why: 문서 업로드 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 컬렉션 문서 쿼리를 무효화합니다.
 * - 실패 시 사용자에게 오류 메시지를 노출합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useCreateDocument = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ collectionId, data }: { collectionId: string; data: DocumentUploadRequest }) =>
      createDocument(collectionId, data),
    onSuccess: (_, { collectionId }) => {
      queryClient.invalidateQueries({ queryKey: documentQueries.all(collectionId) });
      toast.success("성공", { description: "문서가 업로드 되었습니다." });
    },
    onError: async (error) => {
      const message = await getApiErrorMessage(error, "문서 업로드에 실패했습니다.");
      toast.error("오류", { description: message });
    },
  });
};
