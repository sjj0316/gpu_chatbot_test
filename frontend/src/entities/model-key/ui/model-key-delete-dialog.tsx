import { Button } from "@/shared/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/shared/ui/dialog";

import type { ModelApiKeyRead } from "../model";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  row: ModelApiKeyRead | null;
  onConfirm: (row: ModelApiKeyRead) => void | Promise<void>;
  pending?: boolean;
};

export const ModelKeyDeleteDialog = ({
  open,
  onOpenChange,
  row,
  onConfirm,
  pending = false,
}: Props) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>모델 키 삭제</DialogTitle>
        </DialogHeader>

        <div className="py-2">
          {row ? (
            <p className="text-muted-foreground text-sm">
              다음 API Key를 삭제하시겠습니까? <br />
              <span className="font-medium">
                [{row.id}] {row.alias ?? row.model}
              </span>
            </p>
          ) : (
            <p className="text-muted-foreground text-sm">삭제 대상을 찾을 수 없습니다.</p>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={pending}>
            취소
          </Button>
          <Button
            variant="destructive"
            onClick={() => row && onConfirm(row)}
            disabled={pending || !row}
          >
            {pending ? "삭제 중..." : "삭제"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
