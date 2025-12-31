import { kyClient } from "@/shared/api/ky-client";
import { chatRequestSchema, chatResponseSchema } from "../model";

export async function invokeChat(conversationId: number, payload: unknown) {
  const body = chatRequestSchema.parse(payload);
  const res = await kyClient.post(`conversations/${conversationId}/invoke`, { json: body }).json();

  return chatResponseSchema.parse(res);
}
