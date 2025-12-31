import { z } from "zod";
import {
  collectionSchema,
  createCollectionSchema,
  updateCollectionSchema,
  collectionsListResponseSchema,
  collectionsListParamsSchema,
} from "./schemas";

export type Collection = z.infer<typeof collectionSchema>;
export type CreateCollectionRequest = z.infer<typeof createCollectionSchema>;
export type UpdateCollectionRequest = z.infer<typeof updateCollectionSchema>;
export type CreateCollectionResponse = z.infer<typeof collectionSchema>;
export type CollectionsListResponse = z.infer<typeof collectionsListResponseSchema>;
export type CollectionsListParams = z.infer<typeof collectionsListParamsSchema>;
