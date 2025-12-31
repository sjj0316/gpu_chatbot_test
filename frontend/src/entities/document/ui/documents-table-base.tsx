import { Trash2 } from "lucide-react";

import { Button } from "@/shared/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

import type { DocumentFile } from "../model";

type DocumentsTableBaseProps = {
  documents: DocumentFile[];
  onRowClick?: (doc: DocumentFile) => void;
  onDeleteClick?: (doc: DocumentFile) => void;
  deletingId?: string | null;
};

export const DocumentsTableBase = ({
  documents,
  onRowClick,
  onDeleteClick,
  deletingId = null,
}: DocumentsTableBaseProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>파일명</TableHead>
          <TableHead>청크 수</TableHead>
          <TableHead>문자 수</TableHead>
          <TableHead>파일 ID</TableHead>
          <TableHead>작업</TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {documents.length === 0 ? (
          <TableRow>
            <TableCell colSpan={5} className="h-24 text-center">
              <div className="flex flex-col items-center gap-3">
                <p className="text-muted-foreground">문서가 없습니다</p>
              </div>
            </TableCell>
          </TableRow>
        ) : (
          documents.map((doc) => {
            const charCount =
              doc.chunks?.reduce((total, chunk) => total + (chunk.content?.length || 0), 0) ?? 0;

            return (
              <TableRow
                key={doc.file_id}
                className="hover:bg-muted/50 cursor-pointer"
                onClick={() => onRowClick?.(doc)}
              >
                <TableCell>{doc.source || doc.file_id}</TableCell>
                <TableCell>{doc.chunk_count || 0}</TableCell>
                <TableCell>{charCount}</TableCell>
                <TableCell className="font-mono text-xs">{doc.file_id}</TableCell>
                <TableCell onClick={(e) => e.stopPropagation()}>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={deletingId === doc.file_id}
                    onClick={() => onDeleteClick?.(doc)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            );
          })
        )}
      </TableBody>
    </Table>
  );
};
