import { kyClient } from "@/shared/api/ky-client";

/**
 * Why: 사용하지 않는 모델 키를 영구 삭제합니다.
 *
 * Contract:
 * - keyId는 1 이상의 정수여야 합니다.
 *
 * @returns 없음(204).
 */
export const deleteModelKey = async (keyId: number): Promise<void> => {
  await kyClient.delete(`api-keys/${keyId}`);
};
