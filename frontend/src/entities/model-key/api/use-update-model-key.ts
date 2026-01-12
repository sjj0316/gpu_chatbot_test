import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { updateModelKey } from "./update-model-key";
import { type ModelApiKeyUpdate } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

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
