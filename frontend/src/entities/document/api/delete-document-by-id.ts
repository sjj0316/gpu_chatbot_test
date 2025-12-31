import { kyClient } from "@/shared/api/ky-client";

export const deleteDocumentById = async (
  collectionId: string,
  targetId: string,
  deleteBy: "file_id" | "document_id"
): Promise<void> => {
  const searchParams = new URLSearchParams();
  searchParams.append("delete_by", deleteBy);

  await kyClient
    .delete(`collections/${collectionId}/documents/${targetId}?${searchParams.toString()}`)
    .json();
};
