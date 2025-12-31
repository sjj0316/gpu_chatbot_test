import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { ScrollArea } from "@/shared/ui/scroll-area";
import { Separator } from "@/shared/ui/separator";
import { cn } from "@/shared/lib/utils";

import {
  useConversations,
  useDeleteConversation,
  type ConversationListItem,
} from "@/entities/conversation";
import { CreateConversationModal } from "./create-conversation-modal";

export type ConversationSidebarProps = {
  selectedId?: number | null;
  onSelect: (id: number) => void;
};

export function ConversationSidebar({ selectedId, onSelect }: ConversationSidebarProps) {
  const { data, isLoading } = useConversations({ limit: 100, offset: 0 });
  const { mutateAsync: deleteConv, isPending: deleting } = useDeleteConversation();

  const [open, setOpen] = useState(false);

  const handleDelete = async (id: number) => {
    await deleteConv(id);
  };

  const items = (data ?? []) as ConversationListItem[];

  return (
    <div className="flex h-full w-72 flex-col border-r">
      <div className="flex items-center justify-between p-3">
        <div className="font-semibold">대화 목록</div>
        <Button size="icon" variant="ghost" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" />
        </Button>
      </div>
      <Separator />
      <ScrollArea className="flex-1">
        <div className="space-y-1 p-2">
          {isLoading && <div className="p-2 text-xs opacity-60">불러오는 중...</div>}
          {items.map((c) => (
            <div
              key={c.id}
              className={cn(
                "group hover:bg-muted flex cursor-pointer items-center justify-between rounded-md px-3 py-2",
                selectedId === c.id && "bg-muted"
              )}
              onClick={() => onSelect(c.id)}
            >
              <div className="truncate text-sm">{c.title ?? `대화 #${c.id}`}</div>
              <Button
                size="icon"
                variant="ghost"
                className="opacity-0 group-hover:opacity-100"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(c.id);
                }}
                disabled={deleting}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          {!isLoading && items.length === 0 && (
            <div className="p-3 text-xs opacity-60">아직 대화가 없습니다.</div>
          )}
        </div>
      </ScrollArea>

      <CreateConversationModal
        open={open}
        onOpenChange={setOpen}
        onCreated={(id) => {
          setOpen(false);
          onSelect(id);
        }}
      />
    </div>
  );
}
