import { useState } from "react";
import {
  useDeleteMcpServer,
  MCPServersTableBase,
  MCPServerDeleteDialog,
  type MCPServerRead,
} from "@/entities/mcp-server";

type MCPServersTableProps = {
  items: MCPServerRead[];
  onRowClick: (it: MCPServerRead) => void;
  onEditClick: (it: MCPServerRead) => void;
};

export const MCPServersTable = ({ items, onRowClick, onEditClick }: MCPServersTableProps) => {
  const { mutateAsync, isPending } = useDeleteMcpServer();
  const [deleteTarget, setDeleteTarget] = useState<MCPServerRead | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleDeleteClick = (it: MCPServerRead) => {
    setDeleteTarget(it);
    setDialogOpen(true);
  };

  const handleConfirmDelete = async (it: MCPServerRead) => {
    try {
      await mutateAsync(it.id);
    } finally {
      setDialogOpen(false);
      setDeleteTarget(null);
    }
  };

  return (
    <>
      <MCPServersTableBase
        items={items}
        onEdit={onEditClick}
        onDelete={handleDeleteClick}
        onRowClick={onRowClick}
      />

      <MCPServerDeleteDialog
        open={dialogOpen}
        onOpenChange={(open) => {
          if (!open) setDeleteTarget(null);
          setDialogOpen(open);
        }}
        name={deleteTarget?.name ?? ""}
        onConfirm={() => deleteTarget && handleConfirmDelete(deleteTarget)}
        loading={isPending}
      />
    </>
  );
};
