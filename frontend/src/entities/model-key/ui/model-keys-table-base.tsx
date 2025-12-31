import { Edit, Trash2 } from "lucide-react";

import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { ComponentLoading } from "@/shared/ui/component-loading";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";

import type { ModelApiKeyRead } from "../model";

type ModelKeysTableBaseProps = {
  rows: ModelApiKeyRead[];
  isLoading?: boolean;
  loadingRows?: number;
  onEdit?: (row: ModelApiKeyRead) => void;
  onDeleteClick?: (row: ModelApiKeyRead) => void;
  deletingId?: number | null;
};

export const ModelKeysTableBase = ({
  rows,
  isLoading,
  loadingRows = 3,
  onEdit,
  onDeleteClick,
  deletingId = null,
}: ModelKeysTableBaseProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>ID</TableHead>
          <TableHead>별칭</TableHead>
          <TableHead>제공자</TableHead>
          <TableHead>모델</TableHead>
          <TableHead>용도</TableHead>
          <TableHead>공개</TableHead>
          <TableHead>활성</TableHead>
          <TableHead>소유자</TableHead>
          <TableHead>생성일</TableHead>
          <TableHead>작업</TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {isLoading ? (
          Array.from({ length: loadingRows }).map((_, i) => (
            <TableRow key={`skeleton-${i}`}>
              <TableCell colSpan={10}>
                <ComponentLoading />
              </TableCell>
            </TableRow>
          ))
        ) : rows.length === 0 ? (
          <TableRow>
            <TableCell colSpan={10} className="h-24 text-center">
              <div className="flex flex-col items-center gap-3">
                <p className="text-muted-foreground">등록된 모델 키가 없습니다</p>
              </div>
            </TableCell>
          </TableRow>
        ) : (
          rows.map((r) => (
            <TableRow key={r.id}>
              <TableCell className="font-medium">{r.id}</TableCell>
              <TableCell className="max-w-xs truncate">{r.alias ?? "-"}</TableCell>
              <TableCell className="max-w-xs truncate">{r.provider_code ?? "-"}</TableCell>
              <TableCell className="max-w-xs truncate">{r.model}</TableCell>
              <TableCell className="max-w-xs truncate">{r.purpose_code ?? "-"}</TableCell>
              <TableCell>
                <Badge variant={r.is_public ? "default" : "secondary"}>
                  {r.is_public ? "공개" : "비공개"}
                </Badge>
              </TableCell>
              <TableCell>
                <Badge variant={r.is_active ? "default" : "destructive"}>
                  {r.is_active ? "Y" : "N"}
                </Badge>
              </TableCell>
              <TableCell>{r.owner_nickname ?? "-"}</TableCell>
              <TableCell className="max-w-xs truncate">{r.created_at}</TableCell>
              <TableCell>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => onEdit?.(r)}>
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={deletingId === r.id}
                    onClick={() => onDeleteClick?.(r)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))
        )}
      </TableBody>
    </Table>
  );
};
