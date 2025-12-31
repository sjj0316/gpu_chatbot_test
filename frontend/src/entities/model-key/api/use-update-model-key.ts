import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { updateModelKey } from "./update-model-key";
import { type ModelApiKeyUpdate } from "../model";
export const useUpdateModelKey = (id: number) => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ModelApiKeyUpdate) => updateModelKey(id, payload),
    onSuccess: () => {
      toast.success("API Key가 수정되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      toast.error("API Key 수정에 실패했습니다.");
      console.error(e);
    },
  });
};
