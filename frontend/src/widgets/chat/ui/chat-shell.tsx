import { useEffect } from "react";
import { Separator } from "@/shared/ui/separator";
import { Card, CardContent, CardHeader, CardTitle } from "@/shared/ui/card";
import { useHistories, useStreamChat, type ChatRequest } from "@/entities/conversation";
import {
  useChatStore,
  ConversationSidebar,
  MessageList,
  ChatInput,
  ModelKeySwitcher,
  MCPServerSwitcher,
} from "@/features/chat";

export function ChatShell() {
  const {
    selectedConversationId,
    setConversationId,
    streamingText,
    appendStreamingText,
    resetStreamingText,
    addOptimisticUser,
    clearOptimistic,
    selectedModelKeyId,
    selectedMcpServerIds,
    streamingTool,
    appendStreamingTool,
    clearStreamingTool,
  } = useChatStore();

  const { data: histories = [], refetch } = useHistories(
    selectedConversationId ?? 0,
    !!selectedConversationId
  );

  const { start, stop, isStreaming } = useStreamChat(selectedConversationId ?? 0, {
    onEvent: (e) => {
      if (e.event === "token") {
        const token =
          typeof e.data === "object" && e.data && "data" in (e.data as any)
            ? ((e.data as any).data?.content ?? "")
            : "";
        if (token) appendStreamingText(token);
      } else if (e.event === "tool_start") {
        const toolStart = {
          tool_call_id: (e.data as any)?.tool_call_id,
          tool_name: (e.data as any)?.tool_name,
          args: (e.data as any)?.args,
        };
        appendStreamingTool(toolStart);
      } else if (e.event === "tool_end") {
        const toolEnd = {
          tool_call_id: (e.data as any)?.tool_call_id,
          output: (e.data as any)?.output,
        };
        appendStreamingTool(toolEnd);
      } else if (e.event === "done") {
        refetch().finally(() => {
          resetStreamingText();
          clearOptimistic();
          clearStreamingTool();
        });
      } else if (e.event === "error") {
        resetStreamingText();
        clearStreamingTool();
      }
    },
  });

  useEffect(() => {
    resetStreamingText();
    stop();
  }, [selectedConversationId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSend = async (message: string) => {
    if (!selectedConversationId || !message.trim()) return;
    addOptimisticUser(message);
    resetStreamingText();
    const payload: ChatRequest = {
      message,
      model_key_id: selectedModelKeyId ?? undefined,
      mcp_server_ids: selectedMcpServerIds.length ? selectedMcpServerIds : undefined,
    };
    await start(payload);
  };

  return (
    <div className="flex h-[calc(100vh-64px)] w-full">
      <ConversationSidebar selectedId={selectedConversationId} onSelect={setConversationId} />
      <div className="flex flex-1 flex-col">
        <Card className="rounded-none border-0 border-l">
          <CardHeader className="flex flex-row items-center justify-between py-3">
            <CardTitle className="text-base">
              {selectedConversationId
                ? `대화 #${selectedConversationId}`
                : "대화를 선택하거나 생성하세요"}
            </CardTitle>
            <div className="flex items-center gap-2">
              <MCPServerSwitcher />
              <ModelKeySwitcher />
            </div>
          </CardHeader>
          <Separator />
          <CardContent className="flex h-[calc(100vh-64px-48px)] flex-col p-0">
            {!selectedConversationId ? (
              <div className="flex flex-1 items-center justify-center text-sm opacity-60">
                좌측에서 대화를 선택하거나 새로 생성하세요.
              </div>
            ) : (
              <>
                <MessageList
                  items={histories}
                  streamingText={streamingText}
                  liveTools={streamingTool}
                />
                <ChatInput
                  disabled={!selectedConversationId || isStreaming}
                  onSend={handleSend}
                  className="border-t"
                />
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
