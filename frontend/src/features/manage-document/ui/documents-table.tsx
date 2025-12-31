import { useState } from "react";
import {
  useDeleteDocument,
  DocumentsTableBase,
  DocumentDeleteDialog,
  type DocumentFile,
} from "@/entities/document";

type DocumentsTableProps = {
  documents: DocumentFile[];
  collectionId: string;
  onDocumentClick: (doc: DocumentFile) => void;
};

export const DocumentsTable = ({
  documents,
  collectionId,
  onDocumentClick,
}: DocumentsTableProps) => {
  const deleteDocumentMutation = useDeleteDocument();

  const [deleteTarget, setDeleteTarget] = useState<DocumentFile | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const onDeleteClick = (doc: DocumentFile) => {
    setDeleteTarget(doc);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async (doc: DocumentFile) => {
    try {
      await deleteDocumentMutation.mutateAsync({
        collectionId,
        targetId: doc.file_id,
        deleteBy: "file_id",
      });
    } catch (error) {
      console.error("문서 삭제 오류:", error);
    } finally {
      setDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  const pending = deleteDocumentMutation.isPending;

  return (
    <>
      <DocumentsTableBase
        documents={documents}
        onRowClick={onDocumentClick}
        onDeleteClick={onDeleteClick}
        deletingId={pending ? (deleteTarget?.file_id ?? null) : null}
      />

      <DocumentDeleteDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
          setDialogOpen(open);
        }}
        doc={deleteTarget}
        onConfirm={handleConfirmDelete}
        pending={pending}
      />
    </>
  );
};
