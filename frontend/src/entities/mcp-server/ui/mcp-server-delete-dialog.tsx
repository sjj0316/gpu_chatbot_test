import { Button } from "@/shared/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/ui/dialog";

type MCPServerDeleteDialogProps = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  name: string;
  onConfirm: () => void;
  loading?: boolean;
};

export const MCPServerDeleteDialog = ({
  open,
  onOpenChange,
  name,
  onConfirm,
  loading,
}: MCPServerDeleteDialogProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>삭제</DialogTitle>
          <DialogDescription>{name} 을(를) 삭제할까요?</DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            취소
          </Button>
          <Button variant="destructive" onClick={onConfirm} disabled={loading}>
            삭제
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
