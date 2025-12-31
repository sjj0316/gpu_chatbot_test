import { useState } from "react";

import {
  useDeleteDocument,
  ChunksTableBase,
  ChunkDeleteDialog,
  type ChunkItem,
} from "@/entities/document";

type ChunksTableProps = {
  chunks: ChunkItem[];
  collectionId: string;
  onChunkClick: (chunk: ChunkItem) => void;
};

export const ChunksTable = ({ chunks, collectionId, onChunkClick }: ChunksTableProps) => {
  const deleteMutation = useDeleteDocument();

  const [deleteTarget, setDeleteTarget] = useState<ChunkItem | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const onDeleteClick = (chunk: ChunkItem) => {
    setDeleteTarget(chunk);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async (chunk: ChunkItem) => {
    try {
      await deleteMutation.mutateAsync({
        collectionId,
        targetId: chunk.id,
        deleteBy: "document_id",
      });
    } catch (e) {
      console.error("청크 삭제 오류:", e);
    } finally {
      setDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  const pending = deleteMutation.isPending;

  return (
    <>
      <ChunksTableBase
        chunks={chunks}
        onRowClick={onChunkClick}
        onDeleteClick={onDeleteClick}
        deletingId={pending ? (deleteTarget?.id ?? null) : null}
      />

      <ChunkDeleteDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
          setDialogOpen(open);
        }}
        chunk={deleteTarget}
        onConfirm={handleConfirmDelete}
        pending={pending}
      />
    </>
  );
};
