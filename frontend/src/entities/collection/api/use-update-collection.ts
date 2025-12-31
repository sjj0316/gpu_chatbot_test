import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { collectionQueries } from "./collection.queries";
import { updateCollection } from "./update-collection";
import { type CreateCollectionRequest } from "../model";

export const useUpdateCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      collectionId,
      data,
    }: {
      collectionId: string;
      data: Partial<CreateCollectionRequest>;
    }) => updateCollection(collectionId, data),

    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({
        queryKey: collectionQueries.detail(variables.collectionId).queryKey,
      });
      queryClient.invalidateQueries({ queryKey: collectionQueries.all() });
      toast.success("성공", { description: "컬렉션 수정 완료" });
    },
    onError: (error) => {
      toast.error("오류", { description: "컬렉션 수정 실패했습니다." });
    },
  });
};
