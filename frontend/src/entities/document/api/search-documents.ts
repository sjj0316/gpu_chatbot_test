import { kyClient } from "@/shared/api/ky-client";
import { documentsSearchResponseSchema } from "../model";
import type { DocumentSearchRequest, DocumentsSearchResponse } from "../model";

/**
 * Why: 문서/청크를 시맨틱/키워드 방식으로 검색합니다.
 *
 * Contract:
 * - request는 서버의 검색 요청 스키마를 따라야 합니다.
 * - 응답은 검색 결과 스키마로 파싱됩니다.
 *
 * @returns 검색 결과 목록.
 */
export const searchDocuments = async (
  collectionId: string,
  request: DocumentSearchRequest
) => {
  const res = await kyClient
    .post(`collections/${collectionId}/documents/search`, {
      json: request,
    })
    .json();
  return documentsSearchResponseSchema.parse(res);
};
