import { useLayoutEffect, useRef } from "react";

import type { HistoryItem } from "@/entities/conversation";

import { MessageItem } from "./message-item";
import { ToolItem } from "./tool-item";
import { useChatStore } from "../model";

export type MessageListProps = {
  items: HistoryItem[];
  streamingText?: string;
  liveTools?: any;
};

export function MessageList({ items, streamingText, liveTools }: MessageListProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const optimistic = useChatStore((s) => s.optimisticMessages);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.scrollTop = el.scrollHeight;
  }, [items, optimistic, streamingText]);

  return (
    <div ref={ref} className="flex-1 space-y-3 overflow-auto p-4">
      {items.map((m) => {
        //**여기서 분기처리해서 툴인경우 넣을거 */
        if (m.role === "tool") {
          return (
            <ToolItem
              key={`srv-${m.id}`}
              name={m.tool_name ?? "tool"}
              args={m.tool_input}
              output={m.tool_output}
              timestamp={m.timestamp}
              streaming={false}
            />
          );
        }
        return (
          <MessageItem
            key={`srv-${m.id}`}
            role={m.role}
            content={m.content}
            timestamp={m.timestamp}
          />
        );
      })}

      {optimistic.map((m, idx) => (
        <MessageItem key={`opt-${idx}`} role={m.role} content={m.content} timestamp={m.timestamp} />
      ))}

      {liveTools &&
        liveTools.length > 0 &&
        liveTools.map((t) => (
          <ToolItem
            key={`live-${t.tool_call_id}`}
            name={t.tool_name ?? "tool"}
            args={t.args}
            output={t.output}
            timestamp={t.timestamp}
            streaming={t.output === undefined}
          />
        ))}
      {streamingText && streamingText.length > 0 && (
        <MessageItem role="assistant" content={streamingText} />
      )}
    </div>
  );
}
