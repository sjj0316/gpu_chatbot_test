import { kyClient } from "@/shared/api/ky-client";
import { collectionSchema, type Collection, type UpdateCollectionRequest } from "../model";

export const updateCollection = async (
  collectionId: string,
  data: Partial<UpdateCollectionRequest>
): Promise<Collection> => {
  const res = await kyClient.patch(`collections/${collectionId}`, { json: data }).json();
  return collectionSchema.parse(res);
};
