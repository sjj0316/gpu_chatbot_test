import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { collectionQueries } from "./collection.queries";
import { deleteCollection } from "./delete-collection";

/**
 * Why: 컬렉션 삭제 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 전체 목록 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
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
