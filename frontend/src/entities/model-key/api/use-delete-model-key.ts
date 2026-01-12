import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { deleteModelKey } from "./delete-model-key";
import { getApiErrorMessage } from "@/shared/api/error";

export const useDeleteModelKey = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteModelKey(id),
    onSuccess: () => {
      toast.success("API 키가 삭제되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      void (async () => {
        const message = await getApiErrorMessage(e, "API 키 삭제에 실패했습니다.");
        toast.error("API 키 삭제 실패", { description: message });
      })();
      console.error(e);
    },
  });
};
