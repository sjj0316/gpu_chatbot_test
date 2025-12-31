import { useState } from "react";

import { CreateMcpServerModal, MCPServersListView } from "@/features/manage-mcp-server";
import { McpServersHeader } from "./mcp-servers-header";

export const McpServersManager = () => {
  const [createOpen, setCreateOpen] = useState(false);

  return (
    <div className="container mx-auto p-6">
      <McpServersHeader onCreate={() => setCreateOpen(true)} />

      <MCPServersListView />

      <CreateMcpServerModal open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  );
};
