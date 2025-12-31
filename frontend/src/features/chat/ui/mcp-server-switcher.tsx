import { useMemo } from "react";
import { Button } from "@/shared/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/ui/popover";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/ui/command";
import { Checkbox } from "@/shared/ui/checkbox";
import { Badge } from "@/shared/ui/badge";

import { useMcpServers, type MCPServerRead } from "@/entities/mcp-server";
import { useChatStore } from "../model";

export const MCPServerSwitcher = () => {
  const { selectedMcpServerIds, setSelectedMcpServerIds, toggleMcpServerId } = useChatStore();

  const { data } = useMcpServers({ q: null, page: 1, pageSize: 200 });
  const items = data ?? [];

  const selectedCount = selectedMcpServerIds.length;
  const selectedMap = useMemo(() => new Set(selectedMcpServerIds), [selectedMcpServerIds]);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          MCP Servers
          {selectedCount > 0 && <Badge variant="secondary">{selectedCount}</Badge>}
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 p-0" align="end">
        <Command>
          <CommandInput placeholder="검색..." />
          <CommandList>
            <CommandEmpty>결과 없음</CommandEmpty>
            <CommandGroup heading="서버">
              {items.map((it: MCPServerRead) => {
                const checked = selectedMap.has(it.id);
                return (
                  <CommandItem
                    key={it.id}
                    className="flex items-center gap-2"
                    onSelect={() => toggleMcpServerId(it.id)}
                  >
                    <Checkbox checked={checked} onCheckedChange={() => toggleMcpServerId(it.id)} />
                    <div className="min-w-0">
                      <div className="truncate text-sm">{it.name}</div>
                      <div className="text-muted-foreground truncate text-xs">
                        {(it.config as any)?.url ?? ""}
                      </div>
                    </div>
                  </CommandItem>
                );
              })}
            </CommandGroup>
          </CommandList>
          {selectedCount > 0 && (
            <div className="flex items-center justify-between border-t p-2">
              <div className="text-muted-foreground text-xs">{selectedCount}개 선택됨</div>
              <Button variant="ghost" size="sm" onClick={() => setSelectedMcpServerIds([])}>
                초기화
              </Button>
            </div>
          )}
        </Command>
      </PopoverContent>
    </Popover>
  );
};
