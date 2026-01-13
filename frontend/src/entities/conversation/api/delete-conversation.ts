import { kyClient } from "@/shared/api/ky-client";

/**
 * Why: 대화를 삭제해 히스토리를 정리합니다.
 *
 * Contract:
 * - conversationId는 1 이상의 정수여야 합니다.
 *
 * @returns 삭제 성공 여부.
 */
export async function deleteConversation(conversationId: number) {
  const res = await kyClient.delete(`conversations/${conversationId}`).json<{ ok: boolean }>();

  return res.ok === true;
}
