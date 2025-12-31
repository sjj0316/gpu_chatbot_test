import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/shared/ui/dialog";
import { useCreateModelKey, type ModelApiKeyCreate } from "@/entities/model-key";

import { ModelKeyForm } from "./model-key-form";

type Props = {
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export const CreateModelKeyModal = ({ open, onOpenChange }: Props) => {
  const mutation = useCreateModelKey();

  const handleSubmit = (values: ModelApiKeyCreate) => {
    mutation.mutate(values, {
      onSuccess: () => onOpenChange(false),
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-3xl">
        <DialogHeader>
          <DialogTitle>새 API Key 등록</DialogTitle>
        </DialogHeader>

        <ModelKeyForm mode="create" onSubmit={handleSubmit} loading={mutation.isPending} />
      </DialogContent>
    </Dialog>
  );
};
