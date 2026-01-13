import { kyClient } from "@/shared/api/ky-client";
import { chatRequestSchema, chatResponseSchema } from "../model";

/**
 * Why: 단일 요청/응답 방식의 채팅을 처리해 응답을 반환합니다.
 *
 * Contract:
 * - payload는 요청 스키마로 검증됩니다.
 *
 * @returns 응답 메시지.
 */
export async function invokeChat(conversationId: number, payload: unknown) {
  const body = chatRequestSchema.parse(payload);
  const res = await kyClient.post(`conversations/${conversationId}/invoke`, { json: body }).json();

  return chatResponseSchema.parse(res);
}
