import { kyClient } from "@/shared/api/ky-client";
import { type DocumentDeleteRequest } from "../model";

export const deleteDocuments = async (
  collectionId: string,
  data: DocumentDeleteRequest
): Promise<void> => {
  await kyClient
    .delete(`collections/${collectionId}/documents`, {
      json: data,
    })
    .json();
};
