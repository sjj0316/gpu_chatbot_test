import { useMemo } from "react";

import { ModelKeySelectBase } from "./model-key-select-base";
import { useModelKeys } from "../api";

type ModelKeySelectProps = {
  value: string;
  modelKeyType?: "embedding" | "chat";
  onChange: (value: string) => void;
  className?: string;
  placeholder?: string;
  includeEmptyItem?: boolean;
  emptyLabel?: string;
};

export const ModelKeySelect = ({
  value,
  modelKeyType = "embedding",
  onChange,
  className,
  placeholder = "모델 키 선택",
  includeEmptyItem = false,
  emptyLabel = "선택 안 함",
}: ModelKeySelectProps) => {
  const { data, isLoading } = useModelKeys({
    include_public: true,
    purpose_code: modelKeyType,
    is_active: true,
  });

  const options = useMemo(() => {
    const rows = data ?? [];
    const opts = rows.map((k) => ({
      value: `${k.id}`,
      label: `${k.alias ?? "(별칭 없음)"} - ${k.provider_code} (${k.purpose_code})`,
    }));
    return includeEmptyItem ? [{ value: "", label: emptyLabel }, ...opts] : opts;
  }, [data, includeEmptyItem, emptyLabel]);

  return (
    <ModelKeySelectBase
      value={value}
      onChange={onChange}
      items={options}
      className={className}
      placeholder={isLoading ? "로딩 중..." : placeholder}
      disabled={isLoading}
    />
  );
};
