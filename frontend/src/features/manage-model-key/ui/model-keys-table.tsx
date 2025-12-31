import { useState } from "react";

import {
  useDeleteModelKey,
  ModelKeysTableBase,
  ModelKeyDeleteDialog,
  type ModelApiKeyRead,
} from "@/entities/model-key";

type ModelKeysTableProps = {
  rows: ModelApiKeyRead[];
  isLoading?: boolean;
  onEdit: (row: ModelApiKeyRead) => void;
};

export const ModelKeysTable = ({ rows, onEdit, isLoading }: ModelKeysTableProps) => {
  const deleteMutation = useDeleteModelKey();

  const [deleteTarget, setDeleteTarget] = useState<ModelApiKeyRead | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const onDeleteClick = (row: ModelApiKeyRead) => {
    setDeleteTarget(row);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async (row: ModelApiKeyRead) => {
    try {
      await deleteMutation.mutateAsync(row.id);
    } catch (e) {
      console.error("모델 키 삭제 오류:", e);
    } finally {
      setDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  const pending = deleteMutation.isPending;

  return (
    <>
      <ModelKeysTableBase
        rows={rows}
        isLoading={isLoading}
        onEdit={onEdit}
        onDeleteClick={onDeleteClick}
        deletingId={pending ? (deleteTarget?.id ?? null) : null}
      />

      <ModelKeyDeleteDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
          setDialogOpen(open);
        }}
        row={deleteTarget}
        onConfirm={handleConfirmDelete}
        pending={pending}
      />
    </>
  );
};
