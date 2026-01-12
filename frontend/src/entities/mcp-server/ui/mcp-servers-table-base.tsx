import { memo } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import { Button } from "@/shared/ui/button";
import { Badge } from "@/shared/ui/badge";

import type { MCPServerRead } from "../model";

type MCPServersTableBaseProps = {
  items: MCPServerRead[];
  onEdit: (item: MCPServerRead) => void;
  onDelete: (item: MCPServerRead) => void;
  onRowClick?: (item: MCPServerRead) => void;
};

export const MCPServersTableBase = memo(function MCPServersTableBase({
  items,
  onEdit,
  onDelete,
  onRowClick,
}: MCPServersTableBaseProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-16">ID</TableHead>
          <TableHead>이름</TableHead>
          <TableHead>설명</TableHead>
          <TableHead>공용</TableHead>
          <TableHead>Transport</TableHead>
          <TableHead>URL</TableHead>
          <TableHead className="w-40 text-right">액션</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {items.map((it) => (
          <TableRow
            key={it.id}
            onClick={() => onRowClick?.(it)}
            className={onRowClick ? "hover:bg-muted/40 cursor-pointer" : undefined}
          >
            <TableCell>{it.id}</TableCell>
            <TableCell className="font-medium">{it.name}</TableCell>
            <TableCell className="max-w-[420px] truncate">{it.description ?? ""}</TableCell>
            <TableCell>
              <Badge variant={it.is_public ? "default" : "secondary"}>
                {it.is_public ? "공용" : "개인"}
              </Badge>
            </TableCell>
            <TableCell>
              <Badge variant="secondary">{String((it.config as any)?.transport ?? "")}</Badge>
            </TableCell>
            <TableCell className="max-w-[380px] truncate">
              {String((it.config as any)?.url ?? "")}
            </TableCell>
            <TableCell className="space-x-2 text-right" onClick={(e) => e.stopPropagation()}>
              <Button size="sm" variant="outline" onClick={() => onEdit(it)}>
                수정
              </Button>
              <Button size="sm" variant="destructive" onClick={() => onDelete(it)}>
                삭제
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
});
