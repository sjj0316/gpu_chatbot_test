import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { modelKeyQueries } from "./model-key.queries";
import { deleteModelKey } from "./delete-model-key";

export const useDeleteModelKey = () => {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteModelKey(id),
    onSuccess: () => {
      toast.success("API Key가 삭제되었습니다.");
      qc.invalidateQueries({ queryKey: modelKeyQueries.all() });
    },
    onError: (e: unknown) => {
      toast.error("API Key 삭제에 실패했습니다.");
      console.error(e);
    },
  });
};
