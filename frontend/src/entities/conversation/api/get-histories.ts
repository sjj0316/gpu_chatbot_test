import { kyClient } from "@/shared/api/ky-client";
import { z } from "zod";
import { historyItemSchema } from "../model";

const responseSchema = z.array(historyItemSchema);

export async function getHistories(conversationId: number) {
  const res = await kyClient.get(`conversations/${conversationId}/histories`).json();
  return responseSchema.parse(res);
}
