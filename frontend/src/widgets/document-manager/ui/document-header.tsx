import { Plus } from "lucide-react";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/ui/tooltip";

import { CollectionSelect } from "@/features/manage-collection";

type DocumentHeaderProps = {
  title?: string;
  description?: string;
  collectionId: string;
  onUpload: () => void;
  onChangeCollectionId: (v: string) => void;
};

export const DocumentHeader = ({
  title = "문서 관리",
  description = "RAG에 사용할 문서를 업로드하고 관리하세요.",
  collectionId,
  onUpload,
  onChangeCollectionId,
}: DocumentHeaderProps) => {
  const hasCollection = Boolean(collectionId);

  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        <div className="flex gap-2">
          <Tooltip>
            <TooltipTrigger asChild>
              <span>
                <Button onClick={onUpload} disabled={!hasCollection}>
                  <Plus className="mr-2 h-4 w-4" />
                  문서 업로드
                </Button>
              </span>
            </TooltipTrigger>
            {!hasCollection && (
              <TooltipContent>문서를 업로드하려면 컬렉션을 먼저 선택하세요.</TooltipContent>
            )}
          </Tooltip>
        </div>
      </div>

      <div className="mb-4">
        <CollectionSelect
          value={collectionId}
          onChange={(v) => {
            onChangeCollectionId(v);
          }}
        />
      </div>
    </>
  );
};
