import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Textarea } from "@/shared/ui/textarea";
import { cn } from "@/shared/lib/utils";

export type ChatInputProps = {
  disabled?: boolean;
  onSend: (message: string) => void;
  placeholder?: string;
  className?: string;
};

export function ChatInput({ disabled, onSend, placeholder, className }: ChatInputProps) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const v = value.trim();
    if (!v || disabled) return;
    onSend(v);
    setValue("");
  };

  const handleKeyDown: React.KeyboardEventHandler<HTMLTextAreaElement> = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={cn("flex items-end gap-2 border-t p-3", className)}>
      <Textarea
        value={value}
        placeholder={placeholder ?? "메시지를 입력하세요 (Shift+Enter 줄바꿈)"}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        className="max-h-40 min-h-[44px] resize-y"
      />
      <Button onClick={handleSend} disabled={disabled || !value.trim()} className="shrink-0">
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}
