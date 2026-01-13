import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { updateModelKey } from "./update-model-key";
import { type ModelApiKeyUpdate } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

/**
 * Why: 모델 키 업데이트 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - id에 해당하는 키를 수정합니다.
 * - 성공 시 목록 쿼리를 무효화합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useUpdateModelKey = (id: number) => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ModelApiKeyUpdate) => updateModelKey(id, payload),
    onSuccess: () => {
      toast.success("API 키가 수정되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      void (async () => {
        const message = await getApiErrorMessage(e, "API 키 수정에 실패했습니다.");
        toast.error("API 키 수정 실패", { description: message });
      })();
      console.error(e);
    },
  });
};
