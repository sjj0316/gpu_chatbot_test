import { useCallback, useMemo, useRef, useState } from "react";
import { streamChat, type StreamEvent } from "./stream-chat";
import type { ChatRequest } from "../model";

type UseStreamChatOptions = {
  onEvent?: (e: StreamEvent) => void;
};

/**
 * Why: 스트리밍 채팅을 시작/중지하고 상태를 관리합니다.
 *
 * Contract:
 * - 스트리밍 중 재호출은 무시합니다.
 * - stop 호출 시 AbortController로 스트림을 중단합니다.
 *
 * @returns 스트리밍 제어/상태 객체.
 */
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
