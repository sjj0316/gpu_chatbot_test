import { kyClient } from "@/shared/api/ky-client";
import { collectionSchema, type Collection } from "../model";

/**
 * Why: 단일 컬렉션의 상세 정보를 조회합니다.
 *
 * Contract:
 * - collectionId는 UUID 형식이어야 합니다.
 *
 * @returns 컬렉션 상세.
 */
export const getDetailCollection = async (collectionId: string): Promise<Collection> => {
  const res = await kyClient.get(`collections/${collectionId}`).json();
  return collectionSchema.parse(res);
};
