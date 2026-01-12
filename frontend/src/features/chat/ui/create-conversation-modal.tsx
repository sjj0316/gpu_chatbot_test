import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/shared/ui/dialog";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";

import {
  useCreateConversation,
  conversationCreateSchema,
  type ConversationCreate,
} from "@/entities/conversation";
import { ModelKeySelect } from "@/entities/model-key";
import { useChatStore } from "../model";

type CreateConversationModalProps = {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  onCreated?: (id: number) => void;
};

export function CreateConversationModal({
  open,
  onOpenChange,
  onCreated,
}: CreateConversationModalProps) {
  const { mutateAsync, isPending } = useCreateConversation();
  const selectedModelKeyId = useChatStore((s) => s.selectedModelKeyId);
  const setSelectedModelKeyId = useChatStore((s) => s.setSelectedModelKeyId);

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    getValues,
    formState,
    reset,
  } = useForm<ConversationCreate>({
    resolver: zodResolver(conversationCreateSchema),
    mode: "onChange",
    defaultValues: {
      title: "",
      default_model_key_id: selectedModelKeyId ?? undefined,
    },
  });

  useEffect(() => {
    if (!open) return;
    const current = getValues("default_model_key_id");
    if (!current && selectedModelKeyId) {
      setValue("default_model_key_id", selectedModelKeyId, { shouldValidate: true });
    }
  }, [open, selectedModelKeyId, setValue, getValues]);

  const onSubmit = async (data: ConversationCreate) => {
    const res = await mutateAsync(data);
    if (res?.id) {
      onOpenChange(false);
      reset({ title: "", default_model_key_id: selectedModelKeyId ?? undefined });
      onCreated?.(res.id);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>대화 생성</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <Input {...register("title")} placeholder="대화 제목" />
          <ModelKeySelect
            value={watch("default_model_key_id") ? String(watch("default_model_key_id")) : ""}
            modelKeyType="chat"
            onChange={(v) => {
              const next = v ? Number(v) : undefined;
              setValue("default_model_key_id", next, { shouldValidate: true });
              setSelectedModelKeyId(next ?? null);
            }}
            placeholder="기본 API 키 선택(선택)"
          />
        </div>
        <DialogFooter>
          <Button disabled={!formState.isValid || isPending} onClick={handleSubmit(onSubmit)}>
            생성
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
