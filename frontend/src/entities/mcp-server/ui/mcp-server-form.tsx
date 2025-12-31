import { useMemo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Textarea } from "@/shared/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/shared/ui/form";

import { mcpServerCreateSchema, mcpServerUpdateSchema, type MCPServerConfig } from "../model";

type CreateValues = {
  name: string;
  description?: string | null;
  config: MCPServerConfig;
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
              <FormLabel>이름</FormLabel>
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
              <FormLabel>설명</FormLabel>
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
            name="config.transport"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Transport</FormLabel>
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
                <FormLabel>URL</FormLabel>
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
                <FormLabel>headers</FormLabel>
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
