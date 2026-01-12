import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Textarea } from "@/shared/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/shared/ui/dialog";
import { Hint } from "@/shared/ui/hint";
import {
  useUpdateCollection,
  UpdateCollectionRequest,
  updateCollectionSchema,
  type Collection,
} from "@/entities/collection";

type EditCollectionModalProps = {
  collection: Collection | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
};

export const EditCollectionModal = ({
  open,
  onOpenChange,
  collection,
}: EditCollectionModalProps) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, isValid },
  } = useForm<UpdateCollectionRequest>({
    resolver: zodResolver(updateCollectionSchema),
    mode: "onChange",
    defaultValues: {
      name: "",
      description: "",
      is_public: false,
    },
  });

  const updateMutation = useUpdateCollection();

  useEffect(() => {
    if (collection) {
      reset({
        name: collection.name ?? "",
        description: collection.description ?? "",
        is_public: collection.is_public ?? false,
      });
    }
  }, [collection, reset]);

  const onSubmit = (values: UpdateCollectionRequest) => {
    if (!collection?.collection_id) return;

    updateMutation.mutate(
      {
        collectionId: collection.collection_id,
        data: values,
      },
      {
        onSuccess: () => {
          reset();
          onOpenChange(false);
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>컬렉션 수정</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name" className="flex items-center gap-2">
              컬렉션 이름 *
              <Hint text="목록에서 구분하기 쉬운 이름을 입력하세요." />
            </Label>
            <Input id="name" {...register("name")} required />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description" className="flex items-center gap-2">
              설명
              <Hint text="컬렉션의 용도나 내용을 간단히 적어 주세요." />
            </Label>
            <Textarea id="description" rows={3} {...register("description")} />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="isPublic"
              {...register("is_public")}
              className="border-input bg-background ring-offset-background focus-visible:ring-ring h-4 w-4 rounded focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:outline-hidden"
            />
            <Label htmlFor="isPublic" className="flex items-center gap-2 text-sm leading-none font-medium">
              공개 컬렉션으로 설정
              <Hint text="공개 컬렉션은 다른 사용자에게 노출될 수 있습니다." />
            </Label>
          </div>

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              취소
            </Button>
            <Button type="submit" disabled={!isValid || isSubmitting}>
              {isSubmitting ? "수정 중..." : "저장"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
