import { Plus } from "lucide-react";
import { Button } from "@/shared/ui/button";

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
  description = "RAG용 문서를 업로드하고 관리하세요.",
  collectionId,
  onUpload,
  onChangeCollectionId,
}: DocumentHeaderProps) => {
  return (
    <>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="mb-2 text-3xl font-bold">{title}</h1>
          <p className="text-muted-foreground">{description}</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={onUpload}>
            <Plus className="mr-2 h-4 w-4" />
            문서 업로드
          </Button>
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
