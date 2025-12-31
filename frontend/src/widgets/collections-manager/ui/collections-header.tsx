import { Plus } from "lucide-react";
import { Button } from "@/shared/ui/button";

type CollectionsHeaderProps = {
  title?: string;
  description?: string;
  onCreate?: () => void;
};

export const CollectionsHeader = ({
  title = "컬렉션 관리",
  description = "문서 컬렉션을 생성하고 관리하세요.",
  onCreate,
}: CollectionsHeaderProps) => {
  return (
    <div className="mb-6 flex items-center justify-between">
      <div>
        <h1 className="mb-2 text-3xl font-bold">{title}</h1>
        <p className="text-muted-foreground">{description}</p>
      </div>
      <Button onClick={onCreate}>
        <Plus className="mr-2 h-4 w-4" />새 컬렉션
      </Button>
    </div>
  );
};
