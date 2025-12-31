import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";

import { MCPServerForm, useUpdateMcpServer, type MCPServerRead } from "@/entities/mcp-server";

type EditMcpServerModalProps = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  target: MCPServerRead | null;
};

export const EditMcpServerModal = ({ open, onOpenChange, target }: EditMcpServerModalProps) => {
  const { mutateAsync, isPending } = useUpdateMcpServer();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (v: any) => {
    if (!target) return;
    setSubmitting(true);
    try {
      await mutateAsync({ id: target.id, body: v });
      onOpenChange(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>MCP 서버 수정</DialogTitle>
        </DialogHeader>
        {target && (
          <MCPServerForm
            mode="edit"
            initial={{
              name: target.name,
              description: target.description ?? "",
              config: {
                transport: String((target.config as any)?.transport ?? "http") as any,
                url: (target.config as any)?.url ?? "",
              },
            }}
            onSubmit={handleSubmit}
            submitting={isPending || submitting}
          />
        )}
      </DialogContent>
    </Dialog>
  );
};
