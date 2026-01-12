import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Switch } from "@/shared/ui/switch";
import { Textarea } from "@/shared/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/ui/form";
import { Hint } from "@/shared/ui/hint";

import { mcpServerCreateSchema, mcpServerUpdateSchema, type MCPServerConfig } from "../model";

type CreateValues = {
  name: string;
  description?: string | null;
  config: MCPServerConfig;
  is_public?: boolean;
};

type UpdateValues = Partial<CreateValues>;

type MCPServerFormProps =
  | {
      mode: "create";
      initial?: Partial<CreateValues>;
      onSubmit: (v: CreateValues) => void;
      submitting?: boolean;
    }
  | {
      mode: "edit";
      initial: UpdateValues;
      onSubmit: (v: UpdateValues) => void;
      submitting?: boolean;
    };

export const MCPServerForm = (props: MCPServerFormProps) => {
  const schema = props.mode === "create" ? mcpServerCreateSchema : mcpServerUpdateSchema;
  const defaults = useMemo(
    () => ({
      name: "",
      description: "",
      config: { transport: "http", url: "" },
      is_public: false,
      ...(props.initial ?? {}),
    }),
    [props.initial]
  );

  const form = useForm<any>({
    resolver: zodResolver(schema),
    mode: "onChange",
    defaultValues: defaults,
  });

  const onSubmit = form.handleSubmit((v) => props.onSubmit(v));

  return (
    <Form {...form}>
      <form onSubmit={onSubmit} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="flex items-center gap-2">
                이름
                <Hint text="식별을 위한 서버 이름입니다." />
              </FormLabel>
              <FormControl>
                <Input {...field} placeholder="mcp-rag-server" autoComplete="off" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="flex items-center gap-2">
                설명
                <Hint text="서버의 용도나 특징을 간단히 적어 주세요." />
              </FormLabel>
              <FormControl>
                <Textarea {...field} placeholder="용도, 비고" />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField
            control={form.control}
            name="is_public"
            render={({ field }) => (
              <FormItem className="flex items-center justify-between rounded-md border p-3">
                <FormLabel className="mb-0 flex items-center gap-2">
                  공개
                  <Hint text="공개 설정 시 다른 사용자에게 노출될 수 있습니다." />
                </FormLabel>
                <FormControl>
                  <Switch checked={!!field.value} onCheckedChange={field.onChange} />
                </FormControl>
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="config.transport"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="flex items-center gap-2">
                  Transport
                  <Hint text="서버 연결 방식(예: http, streamable_http)을 선택하세요." />
                </FormLabel>
                <Select value={field.value} onValueChange={field.onChange}>
                  <SelectTrigger>
                    <SelectValue placeholder="선택" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="http">http</SelectItem>
                    <SelectItem value="streamable_http">streamable_http</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="config.url"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="flex items-center gap-2">
                  URL
                  <Hint text="MCP 서버 주소를 입력하세요. 예: http://host:8080" />
                </FormLabel>
                <FormControl>
                  <Input {...field} placeholder="http://host:8080" autoComplete="off" />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="config.headers"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="flex items-center gap-2">
                  headers
                  <Hint text="필요한 경우 인증/커스텀 헤더를 JSON 형태로 입력하세요." />
                </FormLabel>
                <FormControl>
                  <Input
                    {...field}
                    placeholder="{
  'X-Internal-Token': '******'
}"
                    autoComplete="off"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <div className="flex justify-end">
          <Button type="submit" disabled={!form.formState.isValid || props.submitting}>
            {props.mode === "create" ? "생성" : "수정"}
          </Button>
        </div>
      </form>
    </Form>
  );
};
