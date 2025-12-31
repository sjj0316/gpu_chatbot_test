import { useEffect, useState } from "react";
import { Input } from "@/shared/ui/input";
import { Button } from "@/shared/ui/button";

type MCPServersHeaderProps = {
  onSearch: (q: string | null) => void;
};

export const MCPServersHeader = ({ onSearch }: MCPServersHeaderProps) => {
  const [text, setText] = useState("");
  useEffect(() => {
    const id = setTimeout(() => onSearch(text.trim() ? text : null), 300);
    return () => clearTimeout(id);
  }, [text, onSearch]);

  return (
    <div className="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
      <Input
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="이름/설명 검색"
        className="md:max-w-sm"
      />
    </div>
  );
};
