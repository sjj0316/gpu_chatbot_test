import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";

type CollectionOption = {
  value: string;
  label: string;
  disabled?: boolean;
};

type CollectionSelectBaseProps = {
  value: string;
  onChange: (value: string) => void;
  items: CollectionOption[];
  className?: string;
  placeholder?: string;
  disabled?: boolean;
};

export const CollectionSelectBase = ({
  value,
  onChange,
  items,
  className = "w-64",
  placeholder = "컬렉션 선택",
  disabled = false,
}: CollectionSelectBaseProps) => {
  return (
    <Select value={value} onValueChange={onChange} disabled={disabled}>
      <SelectTrigger className={className}>
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        {items.map((opt) => (
          <SelectItem key={opt.value} value={opt.value} disabled={opt.disabled}>
            {opt.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};
