import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { collectionQueries } from "./collection.queries";
import { createCollection } from "./create-collection";
import { type CreateCollectionRequest } from "../model";

/**
 * Why: 컬렉션 생성 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 전체 컬렉션 목록을 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useCreateCollection = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateCollectionRequest) => createCollection(data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: collectionQueries.all() });
      toast.success("성공", { description: "컬렉션이 생성 되었습니다." });
    },
    onError: (error) => {
      toast.error("오류", { description: "컬렉션 생성에 실패했습니다." });
    },
  });
};
