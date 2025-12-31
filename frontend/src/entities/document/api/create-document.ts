import { kyClient } from "@/shared/api/ky-client";
import { type DocumentUploadRequest, documentUploadResponseSchema } from "../model";

export const createDocument = async (collectionId: string, data: DocumentUploadRequest) => {
  const formData = new FormData();

  data.files.forEach((file) => {
    formData.append("files", file);
  });

  if (data.metadatas_json) {
    formData.append("metadatas_json", data.metadatas_json);
  }
  if (data.chunk_size) {
    formData.append("chunk_size", data.chunk_size.toString());
  }
  if (data.chunk_overlap) {
    formData.append("chunk_overlap", data.chunk_overlap.toString());
  }
  if (data.model_api_key_id) {
    formData.append("model_api_key_id", data.model_api_key_id.toString());
  }

  const response = await kyClient
    .post(`collections/${collectionId}/documents`, {
      body: formData,
      headers: {
        "Content-Type": undefined, // FormData로 자동 설정
      },
    })
    .json();

  return response;
};
