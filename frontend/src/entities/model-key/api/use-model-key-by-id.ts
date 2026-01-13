import { useQuery } from "@tanstack/react-query";
import { modelKeyQueries } from "./model-key.queries";

/**
 * Why: 특정 모델 키 상세를 React Query로 조회합니다.
 *
 * Contract:
 * - id가 유효하지 않으면 조회를 비활성화합니다.
 *
 * @returns React Query 결과 객체.
 */
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
