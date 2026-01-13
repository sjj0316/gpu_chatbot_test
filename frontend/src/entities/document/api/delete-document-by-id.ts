import { kyClient } from "@/shared/api/ky-client";

/**
 * Why: 단일 문서 또는 파일을 식별자로 삭제합니다.
 *
 * Contract:
 * - deleteBy는 "file_id" 또는 "document_id"만 허용합니다.
 *
 * @returns 없음(204).
 */
export const deleteDocumentById = async (
  collectionId: string,
  targetId: string,
  deleteBy: "file_id" | "document_id"
): Promise<void> => {
  const searchParams = new URLSearchParams();
  searchParams.append("delete_by", deleteBy);

  await kyClient.delete(
    `collections/${collectionId}/documents/${targetId}?${searchParams.toString()}`
  );
};
