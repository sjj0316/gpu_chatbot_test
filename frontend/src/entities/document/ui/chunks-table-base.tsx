import { Trash2 } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import type { ChunkItem } from "@/entities/document";

type ChunksTableBaseProps = {
  chunks: ChunkItem[];
  onRowClick?: (chunk: ChunkItem) => void;
  onDeleteClick?: (chunk: ChunkItem) => void;
  deletingId?: string | null;
};

export const ChunksTableBase = ({
  chunks,
  onRowClick,
  onDeleteClick,
  deletingId = null,
}: ChunksTableBaseProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>청크 ID</TableHead>
          <TableHead>내용 미리보기</TableHead>
          <TableHead>문자 수</TableHead>
          <TableHead>소스</TableHead>
          <TableHead>작업</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {chunks.length === 0 ? (
          <TableRow>
            <TableCell colSpan={5} className="h-24 text-center">
              <div className="flex flex-col items-center gap-3">
                <p className="text-muted-foreground">청크가 없습니다</p>
              </div>
            </TableCell>
          </TableRow>
        ) : (
          chunks.map((chunk) => (
            <TableRow
              key={chunk.id}
              className="hover:bg-muted/50 cursor-pointer"
              onClick={() => onRowClick?.(chunk)}
            >
              <TableCell className="font-mono text-xs">{chunk.id}</TableCell>
              <TableCell className="max-w-md truncate">{chunk.content}</TableCell>
              <TableCell>{chunk.content?.length || 0}</TableCell>
              <TableCell>{chunk.metadata?.filename || chunk.metadata?.source || "-"}</TableCell>
              <TableCell onClick={(e) => e.stopPropagation()}>
                <Button
                  variant="ghost"
                  size="sm"
                  disabled={deletingId === chunk.id}
                  onClick={() => onDeleteClick?.(chunk)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};
