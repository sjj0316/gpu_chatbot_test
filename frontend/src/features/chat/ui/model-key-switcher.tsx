import { useMemo } from "react";
import { ModelKeySelect } from "@/entities/model-key";
import { useChatStore } from "../model";

type ModelKeySwitcherProps = {
  className?: string;
};

export function ModelKeySwitcher({ className }: ModelKeySwitcherProps) {
  const selected = useChatStore((s) => s.selectedModelKeyId);
  const setSelected = useChatStore((s) => s.setSelectedModelKeyId);

  const value = useMemo(() => (selected ? String(selected) : ""), [selected]);

  return (
    <div className={className}>
      <ModelKeySelect
        value={value}
        modelKeyType="chat"
        onChange={(v) => setSelected(v ? Number(v) : null)}
        placeholder="API 키 선택"
      />
    </div>
  );
}
