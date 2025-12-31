import { kyClient } from "@/shared/api/ky-client";
import { collectionSchema, type Collection } from "../model";

export const getDetailCollection = async (collectionId: string): Promise<Collection> => {
  const res = await kyClient.get(`collections/${collectionId}`).json();
  return collectionSchema.parse(res);
};
