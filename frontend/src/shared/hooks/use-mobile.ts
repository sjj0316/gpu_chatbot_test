import * as React from "react";

const MOBILE_BREAKPOINT = 768;

/**
 * Why: 뷰포트 폭에 따라 모바일 레이아웃 여부를 판별합니다.
 *
 * Contract:
 * - 브라우저 환경(window)에서만 동작합니다.
 *
 * @returns 모바일 뷰포트 여부.
 */
export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined);

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`);
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    };
    mql.addEventListener("change", onChange);
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return !!isMobile;
}
