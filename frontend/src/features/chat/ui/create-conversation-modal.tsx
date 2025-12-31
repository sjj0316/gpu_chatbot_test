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

  const { register, handleSubmit, setValue, watch, formState, reset } = useForm<ConversationCreate>(
    {
      resolver: zodResolver(conversationCreateSchema),
      mode: "onChange",
      defaultValues: { title: "", default_model_key_id: undefined },
    }
  );

  const onSubmit = async (data: ConversationCreate) => {
    const res = await mutateAsync(data);
    if (res?.id) {
      onOpenChange(false);
      reset();
      onCreated?.(res.id);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>새 대화</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">
          <Input {...register("title")} placeholder="대화 제목" />
          <ModelKeySelect
            value={watch("default_model_key_id") ? String(watch("default_model_key_id")) : ""}
            modelKeyType="chat"
            onChange={(v) =>
              setValue("default_model_key_id", v ? Number(v) : undefined, { shouldValidate: true })
            }
            placeholder="기본 API Key 선택(선택)"
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
