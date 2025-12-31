import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";

import { useUpdateModelKey, type ModelApiKeyRead, ModelApiKeyUpdate } from "@/entities/model-key";
import { ModelKeyForm } from "./model-key-form";

type Props = {
  row: ModelApiKeyRead;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export const EditModelKeyModal = ({ row, open, onOpenChange }: Props) => {
  const mutation = useUpdateModelKey(row.id);

  const handleSubmit = (values: ModelApiKeyUpdate) => {
    mutation.mutate(values, {
      onSuccess: () => onOpenChange(false),
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>API Key 수정</DialogTitle>
        </DialogHeader>

        <ModelKeyForm
          mode="update"
          defaultValues={{
            alias: row.alias ?? undefined,
            provider_code: row.provider_code ?? undefined,
            model: row.model,
            endpoint_url: row.endpoint_url ?? undefined,
            purpose_code: row.purpose_code ?? undefined,
            is_public: row.is_public,
            is_active: row.is_active,
            extra: row.extra ?? undefined,
          }}
          onSubmit={handleSubmit}
          loading={mutation.isPending}
        />
      </DialogContent>
    </Dialog>
  );
};
