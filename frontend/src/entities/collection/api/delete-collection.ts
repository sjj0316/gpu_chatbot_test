import { kyClient } from "@/shared/api/ky-client";

export const deleteCollection = async (collectionId: string): Promise<void> => {
  await kyClient.delete(`collections/${collectionId}`).json();
};
