import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/ui/alert-dialog";
import type { ChunkItem } from "@/entities/document";

export type ChunkDeleteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  chunk: ChunkItem | null;
  onConfirm: (chunk: ChunkItem) => void;
  pending?: boolean;
};

export const ChunkDeleteDialog = ({
  open,
  onOpenChange,
  chunk,
  onConfirm,
  pending = false,
}: ChunkDeleteDialogProps) => {
  const desc = chunk
    ? `“${chunk.id}” 청크를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`
    : "선택된 청크가 없습니다.";

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>청크 삭제</AlertDialogTitle>
          <AlertDialogDescription>{desc}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={pending}>취소</AlertDialogCancel>
          <AlertDialogAction
            disabled={!chunk || pending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            onClick={() => chunk && onConfirm(chunk)}
          >
            삭제
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
