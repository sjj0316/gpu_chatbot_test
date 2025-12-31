import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Switch } from "@/shared/ui/switch";
import type { AiModelKeysListParams } from "@/entities/model-key";

type Props = {
  onCreate: () => void;
  filters: AiModelKeysListParams;
  onChangeFilters: (f: AiModelKeysListParams) => void;
};

export const ModelKeysHeader = ({ onCreate, filters, onChangeFilters }: Props) => {
  return (
    <div className="mb-6 flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
      <h1 className="text-xl font-semibold">Model API Keys</h1>

      <div className="flex flex-col gap-3 md:flex-row md:items-end">
        <div className="flex flex-col gap-1">
          <Label htmlFor="provider_code">Provider</Label>
          <Input
            id="provider_code"
            placeholder="openai / anthropic ..."
            defaultValue={filters.provider_code ?? ""}
            onChange={(e) =>
              onChangeFilters({
                ...filters,
                provider_code: e.target.value || undefined,
              })
            }
            className="md:w-48"
          />
        </div>

        <div className="flex flex-col gap-1">
          <Label htmlFor="purpose_code">Purpose</Label>
          <Input
            id="purpose_code"
            placeholder="chat / embedding ..."
            defaultValue={filters.purpose_code ?? ""}
            onChange={(e) =>
              onChangeFilters({
                ...filters,
                purpose_code: e.target.value || undefined,
              })
            }
            className="md:w-48"
          />
        </div>

        <div className="flex items-center gap-2 pt-6">
          <Switch
            checked={filters.include_public ?? true}
            onCheckedChange={(v) => onChangeFilters({ ...filters, include_public: v })}
          />
          <Label className="cursor-pointer">공개 키 포함</Label>
        </div>

        <div className="flex items-center gap-2 pt-6">
          <Switch
            checked={filters.is_active ?? false}
            onCheckedChange={(v) => onChangeFilters({ ...filters, is_active: v })}
          />
          <Label className="cursor-pointer">활성만</Label>
        </div>

        <Button onClick={onCreate} className="md:ml-2">
          새 키 등록
        </Button>
      </div>
    </div>
  );
};
