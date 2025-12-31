import { kyClient } from "@/shared/api/ky-client";
import { chatChunkSchema, chatRequestSchema, type ChatRequest } from "../model";

export type StreamEvent = {
  event: string;
  data: unknown;
};

const splitSSEFrames = (buffer: string): { frames: string[]; rest: string } => {
  const SEP = /\r?\n\r?\n/;
  const frames: string[] = [];
  let rest = buffer;

  while (true) {
    const m = rest.match(SEP);
    if (!m) break;
    const idx = m.index!;
    const sepLen = m[0].length;
    frames.push(rest.slice(0, idx));
    rest = rest.slice(idx + sepLen);
  }
  return { frames, rest };
};

const normalizeTokenEvent = (evtName: string | null, raw: unknown) => {
  let token = "";
  if (typeof raw === "string") token = raw;
  else if (raw && typeof raw === "object") {
    const any = raw as any;
    token = any?.data?.content ?? any?.text ?? any?.token ?? "";
  }
  return {
    event: "token",
    data: { data: { content: token } },
  } satisfies StreamEvent;
};

export async function streamChat(opts: {
  conversationId: number;
  payload: ChatRequest;
  onEvent: (e: StreamEvent) => void;
  signal?: AbortSignal;
}) {
  const { conversationId, payload, onEvent, signal } = opts;

  const body = chatRequestSchema.parse(payload);

  const res = await kyClient.post(`conversations/${conversationId}/stream`, {
    json: body,
    signal,
    timeout: false,
    headers: {
      Accept: "text/event-stream",
      "Cache-Control": "no-cache",
      "X-Accel-Buffering": "no",
    },
  });

  if (!res.ok || !res.body) {
    throw new Error(`Stream start failed: ${res.status} ${res.statusText}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";
  let currentEvent: string | null = null;

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const { frames, rest } = splitSSEFrames(buffer);
      buffer = rest;

      for (const rawFrame of frames) {
        if (!rawFrame.trim()) continue;

        const lines = rawFrame.split(/\r?\n/);
        let dataLine = "";

        for (const line of lines) {
          if (line.startsWith("event:")) currentEvent = line.slice(6).trim();
          else if (line.startsWith("data:")) dataLine += line.slice(5).trim();
        }

        if (!dataLine) {
          currentEvent = null;
          continue;
        }

        try {
          const json = JSON.parse(dataLine);

          if ((currentEvent ?? "").toLowerCase() === "token") {
            onEvent(normalizeTokenEvent(currentEvent, json));
          } else {
            const maybe = chatChunkSchema.safeParse(json);
            onEvent({
              event: currentEvent ?? (maybe.success ? maybe.data.type : "message"),
              data: json,
            });
          }
        } catch {
          if ((currentEvent ?? "").toLowerCase() === "token") {
            onEvent(normalizeTokenEvent(currentEvent, dataLine));
          } else {
            onEvent({ event: currentEvent ?? "message", data: dataLine });
          }
        }

        currentEvent = null;
      }
    }

    if (buffer.trim()) {
      const { frames } = splitSSEFrames(buffer + "\n\n");
      for (const rawFrame of frames) {
        if (!rawFrame.trim()) continue;
        const lines = rawFrame.split(/\r?\n/);
        let dataLine = "";
        let evt: string | null = null;
        for (const line of lines) {
          if (line.startsWith("event:")) evt = line.slice(6).trim();
          else if (line.startsWith("data:")) dataLine += line.slice(5).trim();
        }
        if (!dataLine) continue;

        try {
          const json = JSON.parse(dataLine);
          if ((evt ?? "").toLowerCase() === "token") onEvent(normalizeTokenEvent(evt, json));
          else onEvent({ event: evt ?? "message", data: json });
        } catch {
          if ((evt ?? "").toLowerCase() === "token") onEvent(normalizeTokenEvent(evt, dataLine));
          else onEvent({ event: evt ?? "message", data: dataLine });
        }
      }
    }
  } finally {
    try {
      reader.releaseLock();
    } catch {
      console.log("err");
    }
  }
}
