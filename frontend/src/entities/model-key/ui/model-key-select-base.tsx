import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";

type ModelKeyOption = {
  value: string;
  label: string;
  disabled?: boolean;
};

type ModelKeySelectBaseProps = {
  value: string;
  onChange: (value: string) => void;
  items: ModelKeyOption[];
  className?: string;
  placeholder?: string;
  disabled?: boolean;
};

export const ModelKeySelectBase = ({
  value,
  onChange,
  items,
  className = "w-64",
  placeholder = "모델 키 선택",
  disabled = false,
}: ModelKeySelectBaseProps) => {
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
