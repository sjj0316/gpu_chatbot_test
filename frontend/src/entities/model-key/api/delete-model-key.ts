import { kyClient } from "@/shared/api/ky-client";

export const deleteModelKey = async (keyId: number): Promise<void> => {
  await kyClient.delete(`api-keys/${keyId}`);
};
