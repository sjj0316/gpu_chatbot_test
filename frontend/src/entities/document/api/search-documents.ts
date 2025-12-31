import { kyClient } from "@/shared/api/ky-client";
import { documentsSearchResponseSchema } from "../model";
import type { DocumentSearchRequest, DocumentsSearchResponse } from "../model";

export const searchDocuments = async (collectionId: string, request: DocumentSearchRequest) => {
  const res = await kyClient
    .post(`collections/${collectionId}/documents/search`, {
      json: request,
    })
    .json();
  return documentsSearchResponseSchema.parse(res);
};
