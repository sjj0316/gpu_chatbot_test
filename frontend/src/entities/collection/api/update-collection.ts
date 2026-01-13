import { kyClient } from "@/shared/api/ky-client";
import { collectionSchema, type Collection, type UpdateCollectionRequest } from "../model";

/**
 * Why: 컬렉션 메타데이터를 수정합니다.
 *
 * Contract:
 * - data는 수정 가능한 필드의 부분 집합입니다.
 *
 * @returns 수정된 컬렉션 상세.
 */
export const updateCollection = async (
  collectionId: string,
  data: Partial<UpdateCollectionRequest>
): Promise<Collection> => {
  const res = await kyClient.patch(`collections/${collectionId}`, { json: data }).json();
  return collectionSchema.parse(res);
};
