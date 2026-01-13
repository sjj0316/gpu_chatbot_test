import { kyClient } from "@/shared/api/ky-client";
import {
  type DocumentsListParams,
  type PaginatedChunkResponse,
  type PaginatedDocumentResponse,
  paginatedChunkResponseSchema,
  paginatedDocumentResponseSchema,
} from "../model";

/**
 * Why: 컬렉션 내 문서/청크 목록을 조회합니다.
 *
 * Contract:
 * - params.view가 "chunk"이면 청크 응답 스키마로 파싱합니다.
 *
 * @returns 문서 또는 청크 목록 응답.
 */
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
