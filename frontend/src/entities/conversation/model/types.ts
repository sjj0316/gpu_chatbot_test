import {
  conversationCreateSchema,
  conversationReadSchema,
  conversationListItemSchema,
  historyItemSchema,
  chatRequestSchema,
  chatChunkSchema,
  chatResponseSchema,
} from "./schemas";

export type ConversationCreate = typeof conversationCreateSchema._type;
export type ConversationRead = typeof conversationReadSchema._type;
export type ConversationListItem = typeof conversationListItemSchema._type;
export type HistoryItem = typeof historyItemSchema._type;
export type ChatRequest = typeof chatRequestSchema._type;
export type ChatChunk = typeof chatChunkSchema._type;
export type ChatResponse = typeof chatResponseSchema._type;
