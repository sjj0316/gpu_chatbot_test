import { useMemo, useState } from "react";

import { Spinner } from "@/shared/ui/spinner";
import { FooterPagination } from "@/shared/ui/pagination";
import {
  useMcpServers,
  MCPServersTableBase,
  MCPServerDeleteDialog,
  type MCPServerRead,
} from "@/entities/mcp-server";

import { MCPServersTable } from "./mcp-servers-table";
import { MCPServersHeader } from "./mcp-servers-header";
import { EditMcpServerModal } from "./edit-mcp-server-modal";
import { ViewMcpServerModal } from "./view-mcp-server-modal";

export const MCPServersListView = () => {
  const [q, setQ] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(20);

  const params = useMemo(() => ({ q, page, pageSize: limit }), [q, page, limit]);
  const { data, isLoading, isFetching } = useMcpServers(params);

  const items = data ?? [];
  const hasNext = items.length === limit;
  const totalCount = (page - 1) * limit + items.length + (hasNext ? limit : 0);

  const [selected, setSelected] = useState<MCPServerRead | null>(null);
  const [viewOpen, setViewOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);

  const handleRowClick = (it: MCPServerRead) => {
    setSelected(it);
    setViewOpen(true);
  };

  const handleEditClick = (it: MCPServerRead) => {
    setSelected(it);
    setEditOpen(true);
  };

  return (
    <>
      <MCPServersHeader
        onSearch={(v) => {
          setPage(1);
          setQ(v);
        }}
      />

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Spinner size="lg" />
        </div>
      ) : (
        <MCPServersTable items={items} onRowClick={handleRowClick} onEditClick={handleEditClick} />
      )}

      <div className="mt-2 text-sm opacity-70">{isFetching ? "갱신 중..." : ""}</div>

      <FooterPagination page={page} limit={limit} totalCount={totalCount} onPageChange={setPage} />

      <ViewMcpServerModal
        open={viewOpen}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
          setViewOpen(open);
        }}
        target={selected}
      />

      <EditMcpServerModal
        open={editOpen}
        onOpenChange={(open) => {
          if (!open) setSelected(null);
          setEditOpen(open);
        }}
        target={selected}
      />
    </>
  );
};
