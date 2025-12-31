import { FileText, Hash } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";

import type { DocumentChunk } from "../model";

type DocumentCardProps = {
  document: DocumentChunk;
  onView: (document: DocumentChunk) => void;
  onEdit: (document: DocumentChunk) => void;
  onDelete: (documentId: string) => void;
};

export const DocumentCard = ({ document, onView, onEdit, onDelete }: DocumentCardProps) => {
  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg">
            <FileText className="text-primary h-5 w-5" />
            <span className="truncate">{document.metadata.source}</span>
          </CardTitle>
          <div className="flex gap-1">
            <Button variant="ghost" size="sm" onClick={() => onView(document)}>
              상세
            </Button>
            <Button variant="ghost" size="sm" onClick={() => onEdit(document)}>
              편집
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDelete(document.id)}
              className="text-destructive hover:text-destructive"
            >
              삭제
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-muted-foreground mb-2 flex items-center gap-4 text-sm">
          <div className="flex items-center gap-1">
            <Hash className="h-4 w-4" />
            <span>청크 {document.metadata.chunk_index}</span>
          </div>
          <span>페이지 {document.metadata.page_number}</span>
          <span>파일 ID: {document.metadata.file_id.substring(0, 8)}...</span>
        </div>
        <p className="text-muted-foreground line-clamp-2 text-sm">{document.content}</p>
      </CardContent>
    </Card>
  );
};
