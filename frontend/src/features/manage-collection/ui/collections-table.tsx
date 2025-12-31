import { useState } from "react";

import {
  useDeleteCollection,
  CollectionsTableBase,
  CollectionDeleteDialog,
  type Collection,
} from "@/entities/collection";

type CollectionsTableProps = {
  collections: Collection[];
  isLoading?: boolean;
  onEdit: (collection: Collection) => void;
};

export const CollectionsTable = ({ collections, onEdit, isLoading }: CollectionsTableProps) => {
  const deleteCollectionMutation = useDeleteCollection();

  const [deleteTarget, setDeleteTarget] = useState<Collection | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const onDeleteClick = (row: Collection) => {
    setDeleteTarget(row);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async (row: Collection) => {
    try {
      await deleteCollectionMutation.mutateAsync(row.collection_id);
    } catch (e) {
      console.error("컬렉션 삭제 오류:", e);
    } finally {
      setDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  const pending = deleteCollectionMutation.isPending;

  return (
    <>
      <CollectionsTableBase
        collections={collections}
        isLoading={isLoading}
        onEdit={onEdit}
        onDeleteClick={onDeleteClick}
        deletingId={pending ? (deleteTarget?.collection_id ?? null) : null}
      />

      <CollectionDeleteDialog
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
