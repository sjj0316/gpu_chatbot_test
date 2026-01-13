/**
 * Why: 날짜를 UI 표시에 적합한 로컬 포맷으로 변환합니다.
 *
 * Contract:
 * - 유효한 날짜 문자열 또는 Date 인스턴스를 입력해야 합니다.
 *
 * @returns 한국어 로케일 기준의 날짜 문자열.
 */
export const formatDate = (date: string | Date): string => {
  return new Intl.DateTimeFormat("ko-KR").format(new Date(date));
};

/**
 * Why: 긴 텍스트를 UI에서 과도하게 길어지지 않게 제한합니다.
 *
 * Contract:
 * - length는 0 이상이어야 합니다.
 *
 * @returns 길이 제한이 적용된 문자열.
 */
export const truncateText = (text: string, length: number = 100): string => {
  if (text.length <= length) return text;
  return text.substring(0, length) + "...";
};

/**
 * Why: 연속 호출을 묶어 이벤트 핸들러 과다 호출을 방지합니다.
 *
 * Contract:
 * - 마지막 호출 이후 wait(ms) 경과 시에만 실행됩니다.
 *
 * @returns 디바운스 처리된 함수.
 */
export const debounce = <T extends (...args: any[]) => any>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};
