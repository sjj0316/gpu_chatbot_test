import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { createModelKey } from "./create-model-key";
import { type ModelApiKeyCreate } from "../model";
import { getApiErrorMessage } from "@/shared/api/error";

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
