import { Edit, Trash2 } from "lucide-react";
import { Badge } from "@/shared/ui/badge";
import { Button } from "@/shared/ui/button";
import { ComponentLoading } from "@/shared/ui/component-loading";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/ui/table";
import type { Collection } from "../model";

type CollectionsTableBaseProps = {
  collections: Collection[];
  isLoading?: boolean;
  loadingRows?: number;
  onEdit?: (row: Collection) => void;
  onDeleteClick?: (row: Collection) => void;
  deletingId?: string | null;
};

export const CollectionsTableBase = ({
  collections,
  isLoading,
  loadingRows = 3,
  onEdit,
  onDeleteClick,
  deletingId = null,
}: CollectionsTableBaseProps) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>컬렉션명</TableHead>
          <TableHead>설명</TableHead>
          <TableHead>임베딩 모델</TableHead>
          <TableHead>차원 수</TableHead>
          <TableHead>공개여부</TableHead>
          <TableHead>문서 수</TableHead>
          <TableHead>청크 수</TableHead>
          <TableHead>작업</TableHead>
        </TableRow>
      </TableHeader>

      <TableBody>
        {isLoading ? (
          Array.from({ length: loadingRows }).map((_, i) => (
            <TableRow key={`skeleton-${i}`}>
              <TableCell colSpan={8}>
                <ComponentLoading />
              </TableCell>
            </TableRow>
          ))
        ) : collections.length === 0 ? (
          <TableRow>
            <TableCell colSpan={8} className="h-24 text-center">
              <div className="flex flex-col items-center gap-3">
                <p className="text-muted-foreground">컬렉션이 없습니다</p>
              </div>
            </TableCell>
          </TableRow>
        ) : (
          collections.map((collection) => (
            <TableRow key={collection.collection_id}>
              <TableCell className="font-medium">{collection.name}</TableCell>
              <TableCell className="max-w-xs truncate">{collection.description || "-"}</TableCell>
              <TableCell className="max-w-xs truncate">
                {collection.embedding_model || "-"}
              </TableCell>
              <TableCell className="max-w-xs truncate">
                {collection.embedding_dimension || "-"}
              </TableCell>
              <TableCell>
                <Badge variant={collection.is_public ? "default" : "secondary"}>
                  {collection.is_public ? "공개" : "비공개"}
                </Badge>
              </TableCell>
              <TableCell>{collection.document_count}</TableCell>
              <TableCell>{collection.chunk_count}</TableCell>
              <TableCell>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm" onClick={() => onEdit?.(collection)}>
                    <Edit className="h-4 w-4" />
                  </Button>

                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={deletingId === collection.collection_id}
                    onClick={() => onDeleteClick?.(collection)}
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
