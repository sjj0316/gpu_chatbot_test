import { Button } from "@/shared/ui/button";
import { Separator } from "@/shared/ui/separator";

type HeaderProps = {
  onCreate: () => void;
};

export const McpServersHeader = ({ onCreate }: HeaderProps) => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">MCP 서버 관리</h2>
          <p className="text-muted-foreground text-sm">
            MCP 서버를 등록하고 수정/삭제할 수 있습니다.
          </p>
        </div>
        <Button onClick={onCreate}>신규 등록</Button>
      </div>
      <Separator />
    </div>
  );
};
