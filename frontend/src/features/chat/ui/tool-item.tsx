import { cn } from "@/shared/lib/utils";

export type ToolItemProps = {
  name: string;
  args?: any;
  output?: any;
  timestamp?: string;
  streaming?: boolean; // 스트리밍 중 여부
  className?: string;
};

function pretty(obj: any) {
  try {
    if (typeof obj === "string") {
      const maybe = JSON.parse(obj);
      return JSON.stringify(maybe, null, 2);
    }
    return JSON.stringify(obj, null, 2);
  } catch {
    return typeof obj === "string" ? obj : String(obj);
  }
}

export function ToolItem({ name, args, output, timestamp, streaming, className }: ToolItemProps) {
  return (
    <div
      className={cn(
        "bg-secondary text-secondary-foreground w-full max-w-[680px] rounded-2xl px-4 py-3 text-sm",
        "border-border border shadow-sm",
        className
      )}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span aria-hidden>🛠️</span>
          <span className="font-medium">{name || "tool"}</span>
          {streaming && <span className="ml-1 animate-pulse text-xs opacity-70">실행 중…</span>}
        </div>
        {timestamp && <div className="text-[10px] opacity-60">{timestamp}</div>}
      </div>

      {args !== undefined && (
        <details className="group mt-2">
          <summary
            className={cn(
              "flex cursor-pointer list-none items-center justify-between rounded-md px-2 py-1",
              "hover:bg-background/40 transition-colors"
            )}
          >
            <span className="text-[11px] tracking-wide uppercase opacity-70">args</span>
            <span className="text-xs opacity-60 transition-transform group-open:rotate-180">▾</span>
          </summary>
          <pre
            className={cn(
              "bg-background/60 mt-1 overflow-auto rounded-md p-2 font-mono text-xs",
              "max-h-64" // 내용이 길면 내부 스크롤
            )}
          >
            {pretty(args)}
          </pre>
        </details>
      )}

      {output !== undefined && (
        <details className="group mt-2" open={streaming /* 실행 완료 시 기본 펼침 */}>
          <summary
            className={cn(
              "flex cursor-pointer list-none items-center justify-between rounded-md px-2 py-1",
              "hover:bg-background/40 transition-colors"
            )}
          >
            <span className="text-[11px] tracking-wide uppercase opacity-70">output</span>
            <span className="text-xs opacity-60 transition-transform group-open:rotate-180">▾</span>
          </summary>
          <pre
            className={cn(
              "bg-background/60 mt-1 overflow-auto rounded-md p-2 font-mono text-xs",
              "max-h-64"
            )}
          >
            {pretty(output)}
          </pre>
        </details>
      )}
    </div>
  );
}
