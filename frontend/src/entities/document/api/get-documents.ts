import { kyClient } from "@/shared/api/ky-client";
import {
  type DocumentsListParams,
  type PaginatedChunkResponse,
  type PaginatedDocumentResponse,
  paginatedChunkResponseSchema,
  paginatedDocumentResponseSchema,
} from "../model";

export const getDocuments = async (
  collectionId: string,
  params?: DocumentsListParams
): Promise<PaginatedDocumentResponse | PaginatedChunkResponse> => {
  const res = await kyClient
    .get(`collections/${collectionId}/documents`, {
      searchParams: params as Record<string, string | number | boolean>,
    })
    .json();

  if (params?.view === "chunk") {
    return paginatedChunkResponseSchema.parse(res);
  }
  return paginatedDocumentResponseSchema.parse(res);
};
