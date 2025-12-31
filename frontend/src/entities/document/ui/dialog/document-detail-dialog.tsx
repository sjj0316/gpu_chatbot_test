import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { Badge } from "@/shared/ui/badge";
import { Separator } from "@/shared/ui/separator";
import { ScrollArea } from "@/shared/ui/scroll-area";

import type { DocumentFile } from "../../model";

type DocumentDetailDialogProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  document: DocumentFile;
};

export const DocumentDetailDialog = ({
  isOpen,
  onOpenChange,
  document,
}: DocumentDetailDialogProps) => {
  const totalChars = document.chunks.reduce((sum, chunk) => sum + chunk.content.length, 0);
  const avgCharsPerChunk =
    document.chunk_count > 0 ? Math.round(totalChars / document.chunk_count) : 0;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-4xl">
        <DialogHeader>
          <DialogTitle>문서 상세 정보</DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* 기본 정보 */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-muted-foreground text-sm font-medium">파일명</label>
              <p className="text-sm">{document.source}</p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">파일 ID</label>
              <p className="font-mono text-sm">{document.file_id}</p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">총 청크 수</label>
              <p className="text-sm">{document.chunk_count}개</p>
            </div>
            <div>
              <label className="text-muted-foreground text-sm font-medium">총 문자 수</label>
              <p className="text-sm">{totalChars.toLocaleString()}자</p>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="mb-2 text-sm font-medium">통계</h3>
            <div className="flex gap-4">
              <Badge variant="secondary">평균 문자 수: {avgCharsPerChunk.toLocaleString()}자</Badge>
              <Badge variant="outline">총 문자 수: {totalChars.toLocaleString()}자</Badge>
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="mb-2 text-sm font-medium">청크 목록</h3>
            <ScrollArea className="h-[300px] rounded-md border">
              <div className="space-y-4 p-4">
                {document.chunks.map((chunk, index) => (
                  <div key={chunk.id} className="space-y-2 rounded border p-3">
                    <div className="flex items-center justify-between">
                      <span className="text-muted-foreground font-mono text-sm">
                        청크 {index + 1}: {chunk.id}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {chunk.content.length}자
                      </Badge>
                    </div>
                    <p className="text-muted-foreground line-clamp-3 text-sm">{chunk.content}</p>
                  </div>
                ))}
              </div>
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};
