import { useState } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/shared/ui/dialog";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { Textarea } from "@/shared/ui/textarea";
import { Upload, X } from "lucide-react";

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

export const UploadDocumentModal = ({
  isOpen,
  onOpenChange,
  collectionId,
}: UploadDocumentModalProps) => {
  const [files, setFiles] = useState<File[]>([]);
  const uploadMutation = useCreateDocument();

  const {
    register,
    handleSubmit,
    reset,
    control,
    formState: { isValid, isSubmitting, isDirty },
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
            <Label htmlFor="files">파일 선택</Label>
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

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="chunk_size">청크 크기</Label>
              <Input
                id="chunk_size"
                type="number"
                {...register("chunk_size", { valueAsNumber: true })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="chunk_overlap">청크 오버랩</Label>
              <Input
                id="chunk_overlap"
                type="number"
                {...register("chunk_overlap", { valueAsNumber: true })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="modelKey">모델 키 선택 *</Label>
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
            <Label htmlFor="metadatas_json">메타데이터 (JSON)</Label>
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
              disabled={!isValid || files.length === 0 || uploadMutation.isPending}
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
