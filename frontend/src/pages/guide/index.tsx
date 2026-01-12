import { useEffect, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Textarea } from "@/shared/ui/textarea";
import { Markdown } from "@/shared/ui/markdown";
import { kyClient } from "@/shared/api/ky-client";
import { getApiErrorMessage } from "@/shared/api/error";
import { useAuthStore } from "@/entities/user";

type WikiPage = {
  slug: string;
  title: string;
  content: string;
  updated_at: string | null;
  updated_by: string | null;
};

export const GuidePage = () => {
  const { isAuthenticated } = useAuthStore();
  const [page, setPage] = useState<WikiPage | null>(null);
  const [error, setError] = useState<string>("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [draftTitle, setDraftTitle] = useState("");
  const [draftContent, setDraftContent] = useState("");

  useEffect(() => {
    kyClient
      .get("wiki/guide")
      .json<WikiPage>()
      .then((data) => {
        setPage(data);
        setDraftTitle(data.title);
        setDraftContent(data.content);
      })
      .catch((err) => {
        setError("가이드를 불러올 수 없습니다.");
        console.error("Guide load failed:", err);
      });
  }, []);

  const handleSave = async () => {
    try {
      setIsSaving(true);
      const updated = await kyClient
        .put("wiki/guide", {
          json: {
            title: draftTitle.trim() || "사용 가이드",
            content: draftContent,
          },
        })
        .json<WikiPage>();

      setPage(updated);
      setIsEditing(false);
      toast.success("가이드가 저장되었습니다.");
    } catch (err) {
      const message = await getApiErrorMessage(err, "저장에 실패했습니다.");
      toast.error("가이드 저장 실패", { description: message });
      console.error("Guide save failed:", err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    if (!page) return;
    setDraftTitle(page.title);
    setDraftContent(page.content);
    setIsEditing(false);
  };

  if (error) {
    return (
      <div className="container mx-auto max-w-3xl p-6">
        <div className="text-destructive text-sm">{error}</div>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="container mx-auto max-w-3xl p-6">
        <div className="text-muted-foreground text-sm">가이드를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto max-w-4xl p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">{page.title}</h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {page.updated_at ? `마지막 업데이트: ${new Date(page.updated_at).toLocaleString()}` : ""}
            {page.updated_by ? ` · 수정자: ${page.updated_by}` : ""}
          </p>
        </div>
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                취소
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                {isSaving ? "저장 중..." : "저장"}
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)} disabled={!isAuthenticated}>
              {isAuthenticated ? "편집" : "로그인 필요"}
            </Button>
          )}
        </div>
      </div>

      {isEditing ? (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-3">
            <div className="space-y-2">
              <div className="text-sm font-medium">제목</div>
              <Input value={draftTitle} onChange={(e) => setDraftTitle(e.target.value)} />
            </div>
            <div className="space-y-2">
              <div className="text-sm font-medium">내용 (Markdown)</div>
              <Textarea
                rows={18}
                value={draftContent}
                onChange={(e) => setDraftContent(e.target.value)}
              />
            </div>
          </div>
          <div className="rounded-md border p-4">
            <div className="text-sm font-medium mb-3">미리보기</div>
            <Markdown content={draftContent} />
          </div>
        </div>
      ) : (
        <Markdown content={page.content} />
      )}
    </div>
  );
};
