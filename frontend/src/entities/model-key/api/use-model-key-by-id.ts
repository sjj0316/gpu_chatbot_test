import { useQuery } from "@tanstack/react-query";
import { modelKeyQueries } from "./model-key.queries";

export const useModelKeyDetail = (
  id: number | null | undefined,
  opts?: { reveal_secret?: boolean }
) => {
  const enabled = typeof id === "number" && Number.isFinite(id);
  const safeId = enabled ? (id as number) : 0;

  return useQuery({
    ...modelKeyQueries.detail(safeId, opts),
    enabled,
  });
};
