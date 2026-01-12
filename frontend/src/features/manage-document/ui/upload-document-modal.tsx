import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/shared/ui/dialog";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Textarea } from "@/shared/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/ui/tooltip";
import { Info, Upload, X } from "lucide-react";

import {
  useCreateDocument,
  documentUploadRequestSchema,
  type DocumentUploadRequest,
} from "@/entities/document";
import { ModelKeySelect } from "@/entities/model-key";

type UploadDocumentModalProps = {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  collectionId: string;
};

const Hint = ({ text }: { text: string }) => {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="text-muted-foreground inline-flex cursor-help items-center">
          <Info className="h-3.5 w-3.5" />
        </span>
      </TooltipTrigger>
      <TooltipContent side="top">{text}</TooltipContent>
    </Tooltip>
  );
};

export const UploadDocumentModal = ({
  isOpen,
  onOpenChange,
  collectionId,
}: UploadDocumentModalProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const uploadMutation = useCreateDocument();
  const hasCollection = Boolean(collectionId);

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { isValid, isSubmitting },
  } = useForm<DocumentUploadRequest>({
    resolver: zodResolver(documentUploadRequestSchema),
    mode: "onChange",
    defaultValues: {
      chunk_size: 1000,
      chunk_overlap: 200,
      metadatas_json: "",
      model_api_key_id: 1,
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const onSubmit = (values: DocumentUploadRequest) => {
    if (!hasCollection) {
      toast.error("컬렉션을 선택해주세요.", {
        description: "문서를 업로드하려면 컬렉션이 필요합니다.",
      });
      return;
    }

    if (files.length === 0) return;

    uploadMutation.mutate(
      {
        collectionId,
        data: {
          ...values,
          files,
          metadatas_json: values.metadatas_json || undefined,
        },
      },
      {
        onSuccess: () => {
          onOpenChange(false);
          setFiles([]);
          reset();
        },
      }
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>문서 업로드</DialogTitle>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="files" className="flex items-center gap-2">
              파일 선택
              <Hint text="PDF, TXT, DOCX, MD 파일을 업로드할 수 있습니다." />
            </Label>
            <Input
              id="files"
              type="file"
              multiple
              accept=".pdf,.txt,.docx,.md"
              onChange={handleFileChange}
              className="cursor-pointer"
            />
            {files.length > 0 && (
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div
                    key={index}
                    className="bg-muted flex items-center justify-between rounded-md p-2"
                  >
                    <span className="truncate text-sm">{file.name}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="chunk_size" className="flex items-center gap-2">
                청크 크기
                <Hint text="문서를 나누는 단위 크기입니다. 일반적으로 500~1500 사이를 권장합니다." />
              </Label>
              <Input
                id="chunk_size"
                type="number"
                {...register("chunk_size", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="chunk_overlap" className="flex items-center gap-2">
                청크 오버랩
                <Hint text="인접 청크 간 겹치는 크기입니다. 10~30% 정도가 적당합니다." />
              </Label>
              <Input
                id="chunk_overlap"
                type="number"
                {...register("chunk_overlap", { valueAsNumber: true })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="modelKey" className="flex items-center gap-2">
              모델 키 선택 *
              <Hint text="임베딩에 사용할 API 키를 선택하세요." />
            </Label>
            <Controller
              control={control}
              name="model_api_key_id"
              render={({ field }) => (
                <ModelKeySelect
                  value={field.value ? String(field.value) : ""}
                  onChange={(val) => field.onChange(val ? Number(val) : null)}
                  placeholder="모델 키를 선택하세요"
                />
              )}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="metadatas_json" className="flex items-center gap-2">
              메타데이터(JSON)
              <Hint text="키-값 형식의 추가 정보를 JSON으로 입력할 수 있습니다." />
            </Label>
            <Textarea
              id="metadatas_json"
              rows={3}
              placeholder='{"key": "value"}'
              {...register("metadatas_json")}
            />
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
            <Button
              type="submit"
              disabled={!hasCollection || !isValid || files.length === 0 || uploadMutation.isPending}
            >
              <Upload className="mr-2 h-4 w-4" />
              {uploadMutation.isPending ? "업로드 중..." : "업로드"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
