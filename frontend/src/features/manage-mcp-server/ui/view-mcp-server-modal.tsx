import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { Badge } from "@/shared/ui/badge";
import { Separator } from "@/shared/ui/separator";
import { Spinner } from "@/shared/ui/spinner";

import { useMcpServerById, type MCPServerRead } from "@/entities/mcp-server";

type ViewMcpServerModalProps = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  target: MCPServerRead | null;
};

export const ViewMcpServerModal = ({ open, onOpenChange, target }: ViewMcpServerModalProps) => {
  const id = target?.id ?? null;
  const { data, isLoading, isError } = useMcpServerById(id);

  const detail = data ?? target;
  if (!detail) return null;

  const transport = String((detail.config as any)?.transport ?? "");
  const url = String((detail.config as any)?.url ?? "");
  const reachable = (detail as any)?.runtime?.reachable ?? undefined;
  const tools = (detail as any)?.runtime?.tools ?? [];
  const error = (detail as any)?.runtime?.error ?? null;
  const visibility = detail.is_public ? "공용" : "개인";

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>MCP 서버 상세</DialogTitle>
        </DialogHeader>

        {isLoading ? (
          <div className="flex h-40 items-center justify-center">
            <Spinner size="lg" />
          </div>
        ) : isError ? (
          <div className="text-sm text-red-500">상세 정보를 불러오지 못했습니다.</div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-3 gap-2 text-sm">
              <div className="text-muted-foreground">ID</div>
              <div className="col-span-2">{detail.id}</div>

              <div className="text-muted-foreground">이름</div>
              <div className="col-span-2">{detail.name}</div>

              <div className="text-muted-foreground">설명</div>
              <div className="col-span-2 break-words">{detail.description ?? "-"}</div>

              <div className="text-muted-foreground">공개 범위</div>
              <div className="col-span-2">
                <Badge variant={detail.is_public ? "default" : "secondary"}>
                  {visibility}
                </Badge>
              </div>

              <div className="text-muted-foreground">Transport</div>
              <div className="col-span-2">{transport}</div>

              <div className="text-muted-foreground">URL</div>
              <div className="col-span-2 break-all">{url || "-"}</div>

              <div className="text-muted-foreground">상태</div>
              <div className="col-span-2">
                {reachable === undefined ? (
                  <span className="text-muted-foreground">-</span>
                ) : reachable ? (
                  <Badge variant="secondary">reachable</Badge>
                ) : (
                  <Badge variant="destructive">unreachable</Badge>
                )}
              </div>
            </div>

            <div>
              <div className="mb-2 text-sm font-medium">Tools</div>
              {Array.isArray(tools) && tools.length > 0 ? (
                <div className="space-y-2 rounded-md border p-2">
                  {tools.map((t: any) => (
                    <div key={t.name} className="space-y-1">
                      <div className="flex items-center gap-2">
                        <div className="font-medium">{t.name}</div>
                        {t.description ? (
                          <div className="text-muted-foreground text-xs">{t.description}</div>
                        ) : null}
                      </div>
                      {t.input_schema ? (
                        <pre className="bg-muted max-h-40 overflow-auto rounded p-2 text-xs">
                          {JSON.stringify(t.input_schema, null, 2)}
                        </pre>
                      ) : null}
                      <Separator />
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-muted-foreground text-sm">등록된 도구가 없습니다.</div>
              )}
            </div>

            <div>
              <div className="text-muted-foreground mb-1 text-sm">오류</div>
              <pre className="max-h-32 overflow-auto rounded border p-2 text-xs">
                {error ? String(error) : "-"}
              </pre>
            </div>

            <div>
              <div className="text-muted-foreground mb-1 text-sm">Raw Config</div>
              <pre className="max-h-60 overflow-auto rounded border p-2 text-xs">
                {JSON.stringify(detail.config ?? {}, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};
