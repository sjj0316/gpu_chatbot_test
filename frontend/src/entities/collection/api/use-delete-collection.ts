import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { collectionQueries } from "./collection.queries";
import { deleteCollection } from "./delete-collection";

export const useDeleteCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (collectionId: string) => deleteCollection(collectionId),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: collectionQueries.all() });
      toast.success("성공", { description: "컬렉션 삭제 완료" });
    },
    onError: (error) => {
      toast.error("오류", { description: "컬렉션 삭제 실패했습니다." });
    },
  });
};
