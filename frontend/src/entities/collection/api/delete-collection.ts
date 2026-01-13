import { kyClient } from "@/shared/api/ky-client";

/**
 * Why: 컬렉션을 삭제하고 관련 리소스를 정리합니다.
 *
 * Contract:
 * - collectionId는 UUID 형식이어야 합니다.
 *
 * @returns 없음(204).
 */
export const deleteCollection = async (collectionId: string): Promise<void> => {
  await kyClient.delete(`collections/${collectionId}`);
};
