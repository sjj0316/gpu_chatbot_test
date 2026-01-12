import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { documentQueries } from "./document.queries";
import { createDocument } from "./create-document";
import { type DocumentUploadRequest } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

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
