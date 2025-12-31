import { useCallback, useMemo, useRef, useState } from "react";
import { streamChat, type StreamEvent } from "./stream-chat";
import type { ChatRequest } from "../model";

type UseStreamChatOptions = {
  onEvent?: (e: StreamEvent) => void;
};

export function useStreamChat(conversationId: number, options?: UseStreamChatOptions) {
  const { onEvent } = options ?? {};
  const abortRef = useRef<AbortController | null>(null);

  const [isStreaming, setIsStreaming] = useState(false);
  const [lastEvent, setLastEvent] = useState<StreamEvent | null>(null);
  const [error, setError] = useState<unknown>(null);

  const start = useCallback(
    async (payload: ChatRequest) => {
      if (isStreaming) return;

      setError(null);
      setIsStreaming(true);

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        await streamChat({
          conversationId,
          payload,
          signal: controller.signal,
          onEvent: (e) => {
            setLastEvent(e);
            onEvent?.(e);
          },
        });
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err);
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [conversationId, isStreaming, onEvent]
  );

  const stop = useCallback(() => {
    const c = abortRef.current;
    if (c && !c.signal.aborted) c.abort();
  }, []);

  return useMemo(
    () => ({ start, stop, isStreaming, lastEvent, error }),
    [start, stop, isStreaming, lastEvent, error]
  );
}
