import { useEffect, useMemo } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  modelApiKeyCreateSchema,
  modelApiKeyUpdateSchema,
  MODEL_PROVIDER_OPTIONS,
  MODEL_PURPOSE_OPTIONS,
  type ModelApiKeyCreate,
  type ModelApiKeyUpdate,
} from "@/entities/model-key";

import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Button } from "@/shared/ui/button";
import { Switch } from "@/shared/ui/switch";
import { Textarea } from "@/shared/ui/textarea";
import { Select, SelectTrigger, SelectContent, SelectItem, SelectValue } from "@/shared/ui/select";
import { Hint } from "@/shared/ui/hint";

type Mode = "create" | "update";

type Props = {
  mode: Mode;
  defaultValues?: Partial<ModelApiKeyCreate & ModelApiKeyUpdate>;
  onSubmit: (values: ModelApiKeyCreate | ModelApiKeyUpdate) => void;
  loading?: boolean;
  className?: string;
};

export const ModelKeyForm = ({ mode, defaultValues, onSubmit, loading, className }: Props) => {
  const schema = useMemo(
    () => (mode === "create" ? modelApiKeyCreateSchema : modelApiKeyUpdateSchema),
    [mode]
  );

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ModelApiKeyCreate | ModelApiKeyUpdate>({
    resolver: zodResolver(schema),
    defaultValues,
  });

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  const submitting = loading || isSubmitting;

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className={className ?? "grid grid-cols-1 gap-4 md:grid-cols-2"}
    >
      {/* 별칭 */}
      <div className="space-y-2">
        <Label htmlFor="alias" className="flex items-center gap-2">
          별칭
          <Hint text="식별을 위한 별칭입니다. 동일 사용자 내 중복은 허용되지 않습니다." />
        </Label>
        <Input
          id="alias"
          placeholder="예: default-openai"
          {...register("alias")}
          disabled={submitting}
        />
        {errors.alias && <p className="text-sm text-red-500">{String(errors.alias.message)}</p>}
      </div>

      {/* 제공자 코드 (Select) */}
      <div className="space-y-2">
        <Label className="flex items-center gap-2">
          제공자 코드
          <Hint text="OpenAI, Azure OpenAI 등 제공자 코드를 선택하세요." />
        </Label>
        <Controller
          control={control}
          name={"provider_code" as any}
          render={({ field: { value, onChange } }) => (
            <Select value={value ?? undefined} onValueChange={onChange} disabled={submitting}>
              <SelectTrigger>
                <SelectValue placeholder="제공자를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {MODEL_PROVIDER_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {"provider_code" in errors && (
          <p className="text-sm text-red-500">{String((errors as any).provider_code?.message)}</p>
        )}
      </div>

      {/* 모델 */}
      <div className="space-y-2">
        <Label htmlFor="model" className="flex items-center gap-2">
          모델
          <Hint text="사용할 모델 이름을 입력하세요. 예: gpt-4o-mini, text-embedding-3-small" />
        </Label>
        <Input
          id="model"
          placeholder="gpt-4o-mini / text-embedding-3-small ..."
          {...register("model" as const)}
          disabled={submitting}
        />
        {"model" in errors && (
          <p className="text-sm text-red-500">{String((errors as any).model?.message)}</p>
        )}
      </div>

      {/* 엔드포인트 URL */}
      <div className="space-y-2">
        <Label htmlFor="endpoint_url" className="flex items-center gap-2">
          엔드포인트 URL
          <Hint text="예: https://api.openai.com/v1 또는 https://YOUR_RESOURCE_NAME.openai.azure.com" />
        </Label>
        <Input
          id="endpoint_url"
          placeholder="Example URL: https://api.openai.com/v1"
          {...register("endpoint_url")}
          disabled={submitting}
        />

        {errors.endpoint_url && (
          <p className="text-sm text-red-500">{String(errors.endpoint_url.message)}</p>
        )}
      </div>

      {/* 용도 코드 (Select) */}
      <div className="space-y-2">
        <Label className="flex items-center gap-2">
          용도 코드
          <Hint text="chat 또는 embedding 용도를 선택하세요." />
        </Label>
        <Controller
          control={control}
          name={"purpose_code" as any}
          render={({ field: { value, onChange } }) => (
            <Select value={value ?? undefined} onValueChange={onChange} disabled={submitting}>
              <SelectTrigger>
                <SelectValue placeholder="용도를 선택하세요" />
              </SelectTrigger>
              <SelectContent>
                {MODEL_PURPOSE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        />
        {"purpose_code" in errors && (
          <p className="text-sm text-red-500">{String((errors as any).purpose_code?.message)}</p>
        )}
      </div>

      {/* API Key */}
      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="api_key" className="flex items-center gap-2">
          API Key
          <Hint text="발급받은 비밀키를 입력하세요. 외부에 노출되지 않도록 주의하세요." />
          {mode === "update" && (
            <span className="text-muted-foreground text-xs">(미입력 시 변경 안됨)</span>
          )}
        </Label>
        <Textarea
          id="api_key"
          rows={3}
          placeholder="sk-..."
          {...(register("api_key" as const) as any)}
          disabled={submitting}
        />
        {"api_key" in errors && (
          <p className="text-sm text-red-500">{String((errors as any).api_key?.message)}</p>
        )}
      </div>

      <div className="flex items-center gap-3">
        <Controller
          control={control}
          name={"is_public" as any}
          render={({ field: { value, onChange } }) => (
            <Switch checked={Boolean(value)} onCheckedChange={onChange} disabled={submitting} />
          )}
        />
        <Label className="flex items-center gap-2 cursor-pointer">
          공개 키
          <Hint text="공개 설정 시 다른 사용자에게 노출될 수 있습니다." />
        </Label>
      </div>

      <div className="flex items-center gap-3">
        <Controller
          control={control}
          name={"is_active" as any}
          render={({ field: { value, onChange } }) => (
            <Switch
              checked={Boolean(value ?? true)}
              onCheckedChange={onChange}
              disabled={submitting}
            />
          )}
        />
        <Label className="flex items-center gap-2 cursor-pointer">
          활성화
          <Hint text="비활성화 시 해당 키를 사용할 수 없습니다." />
        </Label>
      </div>

      <div className="space-y-2 md:col-span-2">
        <Label htmlFor="extra" className="flex items-center gap-2">
          추가 설정(JSON)
          <Hint text="추가 옵션이 필요한 경우 JSON 형식으로 입력하세요." />
        </Label>
        <Textarea
          id="extra"
          rows={4}
          placeholder='{"region":"us-east-1"}'
          {...(register("extra" as const, {
            setValueAs: (v) => {
              if (typeof v === "string") {
                const trimmed = v.trim();
                if (trimmed === "") return null;
                try {
                  return JSON.parse(trimmed);
                } catch {
                  return v;
                }
              }
              return v ?? null;
            },
          }) as any)}
          disabled={submitting}
        />
        {errors.extra && <p className="text-sm text-red-500">{String(errors.extra.message)}</p>}
      </div>

      <div className="flex justify-end gap-2 pt-2 md:col-span-2">
        <Button type="submit" disabled={submitting}>
          {mode === "create" ? "생성" : "수정"}
        </Button>
      </div>
    </form>
  );
};
