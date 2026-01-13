import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { createModelKey } from "./create-model-key";
import { type ModelApiKeyCreate } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

/**
 * Why: 모델 키 생성 mutation을 제공해 목록 캐시를 갱신합니다.
 *
 * Contract:
 * - 성공 시 목록 쿼리를 무효화합니다.
 * - 실패 시 오류 메시지를 사용자에게 노출합니다.
 *
 * @returns React Query mutation 객체.
 */
export const useCreateModelKey = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ModelApiKeyCreate) => createModelKey(payload),
    onSuccess: () => {
      toast.success("API 키가 생성되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      void (async () => {
        const message = await getApiErrorMessage(e, "API 키 생성에 실패했습니다.");
        toast.error("API 키 생성 실패", { description: message });
      })();
      console.error(e);
    },
  });
};
