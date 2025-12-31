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

import type { DocumentFile } from "../../model";

type DocumentDeleteDialogProps = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  doc: DocumentFile | null;
  onConfirm: (doc: DocumentFile) => void;
  pending?: boolean;
};

export const DocumentDeleteDialog = ({
  open,
  onOpenChange,
  doc,
  onConfirm,
  pending = false,
}: DocumentDeleteDialogProps) => {
  const title = "문서 삭제";
  const desc = doc
    ? `“${doc.source || doc.file_id}” 문서를 삭제하시겠습니까? 이 작업은 되돌릴 수 없으며, 문서의 모든 청크도 함께 삭제됩니다.`
    : "선택된 문서가 없습니다.";

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{desc}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={pending}>취소</AlertDialogCancel>
          <AlertDialogAction
            disabled={!doc || pending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            onClick={() => doc && onConfirm(doc)}
          >
            삭제
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};
