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
import type { Collection } from "../model";

type CollectionDeleteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  row: Collection | null;
  onConfirm: (row: Collection) => void;
  pending?: boolean;
};

export const CollectionDeleteDialog = ({
  open,
  onOpenChange,
  row,
  onConfirm,
  pending = false,
}: CollectionDeleteDialogProps) => {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>컬렉션 삭제</AlertDialogTitle>
          <AlertDialogDescription>
            {row
              ? `“${row.name}” 컬렉션을 삭제하시겠습니까? 이 작업은 되돌릴 수 없으며, 컬렉션에 포함된 모든 문서도 함께 삭제됩니다.`
              : "선택된 컬렉션이 없습니다."}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={pending}>취소</AlertDialogCancel>
          <AlertDialogAction
            disabled={!row || pending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            onClick={() => row && onConfirm(row)}
          >
            삭제
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
