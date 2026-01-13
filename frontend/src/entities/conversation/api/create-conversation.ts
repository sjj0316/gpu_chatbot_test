import { kyClient } from "@/shared/api/ky-client";
import { conversationCreateSchema, conversationReadSchema } from "../model";

/**
 * Why: 새 대화를 생성해 채팅 컨텍스트를 분리합니다.
 *
 * Contract:
 * - payload는 대화 생성 스키마로 검증됩니다.
 *
 * @returns 생성된 대화 상세.
 */
export async function createConversation(payload: unknown) {
  const body = conversationCreateSchema.parse(payload);
  const res = await kyClient.post(`conversations`, { json: body }).json();
  return conversationReadSchema.parse(res);
}
