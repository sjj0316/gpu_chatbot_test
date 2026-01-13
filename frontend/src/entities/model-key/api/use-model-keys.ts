import { useQuery } from "@tanstack/react-query";

import { modelKeyQueries } from "./model-key.queries";
import { type AiModelKeysListParams } from "../model";

/**
 * Why: 모델 키 목록을 React Query로 캐싱/페이징 조회합니다.
 *
 * Contract:
 * - params가 변경되면 새로운 queryKey로 조회합니다.
 *
 * @returns React Query 결과 객체.
 */
export const useModelKeys = (params?: AiModelKeysListParams) => {
  return useQuery(modelKeyQueries.list(params));
};
