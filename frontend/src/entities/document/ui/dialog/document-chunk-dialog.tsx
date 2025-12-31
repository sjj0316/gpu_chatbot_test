import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { Textarea } from "@/shared/ui/textarea";
import { Label } from "@/shared/ui/label";

import type { ChunkItem } from "../../model";

type DocumentChunkDetailDialogProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  chunk: ChunkItem;
};

export const DocumentChunkDetailDialog = ({
  isOpen,
  onOpenChange,
  chunk,
}: DocumentChunkDetailDialogProps) => {
  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[80vh] max-w-4xl">
        <DialogHeader>
          <DialogTitle>청크 상세 정보</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* 기본 정보 */}
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <Label className="text-muted-foreground">청크 ID</Label>
              <p className="font-mono">{chunk.id}</p>
            </div>
            <div>
              <Label className="text-muted-foreground">파일 ID</Label>
              <p className="font-mono">{chunk.metadata?.file_id || "N/A"}</p>
            </div>
            <div>
              <Label className="text-muted-foreground">파일명</Label>
              <p>{chunk.source || chunk.metadata?.source || "N/A"}</p>
            </div>
          </div>

          {/* 탭 */}
          <Tabs defaultValue="content" className="w-full">
            <TabsList>
              <TabsTrigger value="content">내용</TabsTrigger>
              <TabsTrigger value="metadata">메타데이터</TabsTrigger>
            </TabsList>

            <TabsContent value="content" className="space-y-2">
              <Label>내용</Label>
              <Textarea
                value={chunk.content}
                readOnly
                className="min-h-[400px] font-mono text-sm"
              />
            </TabsContent>

            <TabsContent value="metadata" className="space-y-2">
              <Label>메타데이터</Label>
              <Textarea
                value={JSON.stringify(chunk.metadata, null, 2)}
                readOnly
                className="min-h-[400px] font-mono text-sm"
              />
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};
