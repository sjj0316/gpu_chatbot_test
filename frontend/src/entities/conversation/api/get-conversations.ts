import { kyClient } from "@/shared/api/ky-client";
import { z } from "zod";
import { conversationListItemSchema } from "../model";

const responseSchema = z.array(conversationListItemSchema);

export type GetConversationsParams = {
  limit?: number;
  offset?: number;
};

/**
 * Why: 사용자 대화 목록을 페이지네이션으로 조회합니다.
 *
 * Contract:
 * - limit/offset은 쿼리 파라미터로 전달됩니다.
 *
 * @returns 대화 목록.
 */
export async function getConversations(params: GetConversationsParams = {}) {
  const search = new URLSearchParams();
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const res = await kyClient.get(`conversations?${search.toString()}`).json();
  return responseSchema.parse(res);
}
