import { cn } from "@/shared/lib/utils";

export type MessageItemProps = {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp?: string;
};

export function MessageItem({ role, content, timestamp }: MessageItemProps) {
  const isUser = role === "user";
  const isAssistant = role === "assistant";

  return (
    <div
      className={cn(
        "flex w-full",
        isUser && "justify-end",
        isAssistant && "justify-start",
        !isUser && !isAssistant && "justify-center"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] rounded-2xl px-4 py-2 text-sm whitespace-pre-wrap",
          isUser && "bg-primary text-primary-foreground",
          isAssistant && "bg-muted",
          (role === "system" || role === "tool") && "bg-secondary text-secondary-foreground"
        )}
      >
        <div>{content}</div>
        {timestamp && (
          <div className="mt-1 text-right text-[10px] opacity-60">
            {new Date(timestamp).toLocaleString()}
          </div>
        )}
      </div>
    </div>
  );
}
