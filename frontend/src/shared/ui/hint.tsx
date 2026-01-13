import { Info } from "lucide-react";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/ui/tooltip";

type HintProps = {
  text: string;
};

/**
 * Why: 입력 필드 옆에서 간단한 도움말을 제공하는 아이콘형 툴팁입니다.
 *
 * Props:
 * - text: 표시할 툴팁 문구.
 */
export const Hint = ({ text }: HintProps) => {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="text-muted-foreground inline-flex cursor-help items-center">
          <Info className="h-3.5 w-3.5" />
        </span>
      </TooltipTrigger>
      <TooltipContent side="top">{text}</TooltipContent>
    </Tooltip>
  );
};
