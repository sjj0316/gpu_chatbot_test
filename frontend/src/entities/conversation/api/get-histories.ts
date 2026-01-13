import { kyClient } from "@/shared/api/ky-client";
import { z } from "zod";
import { historyItemSchema } from "../model";

const responseSchema = z.array(historyItemSchema);

/**
 * Why: 대화의 히스토리(메시지/툴 이벤트)를 조회합니다.
 *
 * Contract:
 * - conversationId는 1 이상의 정수여야 합니다.
 *
 * @returns 히스토리 목록.
 */
export async function getHistories(conversationId: number) {
  const res = await kyClient.get(`conversations/${conversationId}/histories`).json();
  return responseSchema.parse(res);
}
