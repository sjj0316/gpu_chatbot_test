import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { createModelKey } from "./create-model-key";
import { type ModelApiKeyCreate } from "../model";

export const useCreateModelKey = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (payload: ModelApiKeyCreate) => createModelKey(payload),
    onSuccess: () => {
      toast.success("API Key가 생성되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      toast.error("API Key 생성에 실패했습니다.");
      console.error(e);
    },
  });
};
