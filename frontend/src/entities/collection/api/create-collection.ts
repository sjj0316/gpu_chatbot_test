import { kyClient } from "@/shared/api/ky-client";
import {
  collectionSchema,
  createCollectionSchema,
  type CreateCollectionRequest,
  type CreateCollectionResponse,
} from "../model";

export const createCollection = async (
  data: CreateCollectionRequest
): Promise<CreateCollectionResponse> => {
  createCollectionSchema.parse(data);
  const res = await kyClient.post("collections", { json: data }).json();
  return collectionSchema.parse(res);
};
