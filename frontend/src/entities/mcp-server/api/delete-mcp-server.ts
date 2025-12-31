import { kyClient } from "@/shared/api/ky-client";

export const deleteMcpServer = async (id: number) => {
  await kyClient.delete(`mcp-servers/${id}`);
  return true;
};
