import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { collectionQueries } from "./collection.queries";
import { updateCollection } from "./update-collection";
import { type CreateCollectionRequest } from "../model";

/**
 * Why: 컬렉션 수정 mutation을 제공해 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 상세/목록 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
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
