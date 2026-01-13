import { kyClient } from "@/shared/api/ky-client";
import {
  collectionSchema,
  createCollectionSchema,
  type CreateCollectionRequest,
  type CreateCollectionResponse,
} from "../model";

/**
 * Why: 새 컬렉션을 생성해 문서/임베딩을 그룹화합니다.
 *
 * Contract:
 * - data는 생성 스키마로 검증됩니다.
 *
 * @returns 생성된 컬렉션 상세.
 */
export const createCollection = async (
  data: CreateCollectionRequest
): Promise<CreateCollectionResponse> => {
  createCollectionSchema.parse(data);
  const res = await kyClient.post("collections", { json: data }).json();
  return collectionSchema.parse(res);
};
