import { kyClient } from "@/shared/api/ky-client";

export async function deleteConversation(conversationId: number) {
  const res = await kyClient.delete(`conversations/${conversationId}`).json<{ ok: boolean }>();

  return res.ok === true;
}
