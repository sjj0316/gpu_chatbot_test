import { kyClient } from "@/shared/api/ky-client";
import { conversationCreateSchema, conversationReadSchema } from "../model";

export async function createConversation(payload: unknown) {
  const body = conversationCreateSchema.parse(payload);
  const res = await kyClient.post(`conversations`, { json: body }).json();
  return conversationReadSchema.parse(res);
}
