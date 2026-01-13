import { kyClient } from "@/shared/api/ky-client";
import { type DocumentDeleteRequest } from "../model";

/**
 * Why: 컬렉션 내 문서를 일괄 삭제합니다.
 *
 * Contract:
 * - file_ids 또는 document_ids 중 하나를 전달해야 합니다.
 *
 * @returns 없음(204).
 */
export const deleteDocuments = async (
  collectionId: string,
  data: DocumentDeleteRequest
): Promise<void> => {
  await kyClient.delete(`collections/${collectionId}/documents`, {
    json: data,
  });
};
