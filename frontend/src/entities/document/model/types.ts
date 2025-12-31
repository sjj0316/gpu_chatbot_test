import { z } from "zod";
import {
  chunkItemSchema,
  documentChunkSchema,
  documentFileSchema,
  paginatedChunkResponseSchema,
  paginatedDocumentResponseSchema,
  documentReadSchema,
  documentUploadRequestSchema,
  documentUploadResponseSchema,
  documentDeleteRequestSchema,
  documentsListParamsSchema,
  documentViewTypeSchema,
  documentSearchTypeSchema,
  documentsSearchRequestSchema,
  documentsSearchResponseItemSchema,
  documentsSearchResponseSchema,
} from "./schemas";

// 단위
export type ChunkItem = z.infer<typeof chunkItemSchema>;
export type DocumentChunk = z.infer<typeof documentChunkSchema>;
export type DocumentFile = z.infer<typeof documentFileSchema>;

// 페이지네이션 응답
export type PaginatedChunkResponse = z.infer<typeof paginatedChunkResponseSchema>;
export type PaginatedDocumentResponse = z.infer<typeof paginatedDocumentResponseSchema>;

// 단순 읽기
export type DocumentRead = z.infer<typeof documentReadSchema>;

// 업로드
export type DocumentUploadRequest = z.infer<typeof documentUploadRequestSchema>;
export type DocumentUploadResponse = z.infer<typeof documentUploadResponseSchema>;

// 삭제
export type DocumentDeleteRequest = z.infer<typeof documentDeleteRequestSchema>;

// 리스트 파라미터/뷰
export type DocumentViewType = z.infer<typeof documentViewTypeSchema>;
export type DocumentsListParams = z.infer<typeof documentsListParamsSchema>;

// 검색
export type DocumentSearchType = z.infer<typeof documentSearchTypeSchema>;
export type DocumentSearchRequest = z.infer<typeof documentsSearchRequestSchema>;
export type DocumentsSearchResponseItem = z.infer<typeof documentsSearchResponseItemSchema>;
export type DocumentsSearchResponse = z.infer<typeof documentsSearchResponseSchema>;
