import { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";

import { MCPServerForm, useCreateMcpServer } from "@/entities/mcp-server";

type CreateMcpServerModalProps = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
};

export const CreateMcpServerModal = ({ open, onOpenChange }: CreateMcpServerModalProps) => {
  const { mutateAsync, isPending } = useCreateMcpServer();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (v: any) => {
    setSubmitting(true);
    try {
      await mutateAsync(v);
      onOpenChange(false);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-xl">
        <DialogHeader>
          <DialogTitle>MCP 서버 생성</DialogTitle>
        </DialogHeader>
        <MCPServerForm mode="create" onSubmit={handleSubmit} submitting={isPending || submitting} />
      </DialogContent>
    </Dialog>
  );
};
