import { kyClient } from "@/shared/api/ky-client";
import { z } from "zod";
import { conversationListItemSchema } from "../model";

const responseSchema = z.array(conversationListItemSchema);

export type GetConversationsParams = {
  limit?: number;
  offset?: number;
};

export async function getConversations(params: GetConversationsParams = {}) {
  const search = new URLSearchParams();
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const res = await kyClient.get(`conversations?${search.toString()}`).json();
  return responseSchema.parse(res);
}
