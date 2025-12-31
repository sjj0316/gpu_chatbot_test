import { useMemo } from "react";

import { useCollections, CollectionSelectBase } from "@/entities/collection";

type CollectionSelectProps = {
  value: string;
  onChange: (value: string) => void;
  className?: string;
  placeholder?: string;
  includeEmptyItem?: boolean;
  emptyLabel?: string;
};

export const CollectionSelect = ({
  value,
  onChange,
  className,
  placeholder = "컬렉션 선택",
  includeEmptyItem = false,
  emptyLabel = "선택 안 함",
}: CollectionSelectProps) => {
  const { data, isLoading } = useCollections();

  const options = useMemo(() => {
    const rows = data?.items ?? [];
    const opts = rows.map((c) => ({
      value: c.collection_id,
      label: `${c.name} - (${c.embedding_model})`,
    }));
    return includeEmptyItem ? [{ value: "", label: emptyLabel }, ...opts] : opts;
  }, [data?.items, includeEmptyItem, emptyLabel]);

  return (
    <CollectionSelectBase
      value={value}
      onChange={onChange}
      items={options}
      className={className}
      placeholder={isLoading ? "로딩 중..." : placeholder}
      disabled={isLoading}
    />
  );
};
