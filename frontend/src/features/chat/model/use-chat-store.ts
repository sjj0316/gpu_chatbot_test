import { create } from "zustand";

type ChatMessage = {
  id?: number;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  timestamp?: string;
};

type ToolData = {
  tool_call_id: string;
  tool_name?: string;
  args?: any;
  output?: any;
};

type ChatState = {
  selectedConversationId: number | null;
  streamingText: string;
  streamingTool: ToolData[];
  isStreaming: boolean;
  error: unknown | null;
  optimisticMessages: ChatMessage[];
  selectedModelKeyId: number | null;
  selectedMcpServerIds: number[];
};

type ChatActions = {
  setConversationId: (id: number | null) => void;
  appendStreamingText: (chunk: string) => void;
  appendStreamingTool: (data: ToolData) => void;
  resetStreamingText: () => void;
  setIsStreaming: (flag: boolean) => void;
  setError: (err: unknown | null) => void;
  addOptimisticUser: (content: string) => void;
  clearOptimistic: () => void;
  setSelectedModelKeyId: (id: number | null) => void;
  setSelectedMcpServerIds: (ids: number[]) => void;
  toggleMcpServerId: (id: number) => void;
  clearMcpServerIds: () => void;
  clearStreamingTool: () => void;
};

export const useChatStore = create<ChatState & ChatActions>((set, get) => ({
  selectedConversationId: null,
  streamingText: "",
  streamingTool: [],
  isStreaming: false,
  error: null,
  optimisticMessages: [],
  selectedModelKeyId: null,
  setConversationId: (id) => set({ selectedConversationId: id }),
  appendStreamingText: (chunk) => set((s) => ({ streamingText: s.streamingText + chunk })),
  resetStreamingText: () => set({ streamingText: "" }),
  setIsStreaming: (flag) => set({ isStreaming: flag }),
  setError: (err) => set({ error: err }),
  selectedMcpServerIds: [],
  setSelectedMcpServerIds: (ids) => set({ selectedMcpServerIds: ids }),
  toggleMcpServerId: (id) => {
    const cur = get().selectedMcpServerIds;
    set({ selectedMcpServerIds: cur.includes(id) ? cur.filter((x) => x !== id) : [...cur, id] });
  },
  appendStreamingTool: (data) => {
    set((s) => {
      const existing = s.streamingTool.find((d) => d.tool_call_id === data.tool_call_id);

      let updated: ToolData[];
      if (existing) {
        updated = s.streamingTool.map((d) =>
          d.tool_call_id === data.tool_call_id ? { ...d, ...data } : d
        );
      } else {
        updated = [...s.streamingTool, data];
      }

      return { streamingTool: updated };
    });
  },
  clearStreamingTool: () => set({ streamingTool: [] }),
  clearMcpServerIds: () => set({ selectedMcpServerIds: [] }),

  addOptimisticUser: (content) =>
    set((s) => ({
      optimisticMessages: [
        ...s.optimisticMessages,
        { role: "user", content, timestamp: new Date().toISOString() },
      ],
    })),
  clearOptimistic: () => set({ optimisticMessages: [] }),
  setSelectedModelKeyId: (id) => set({ selectedModelKeyId: id }),
}));
