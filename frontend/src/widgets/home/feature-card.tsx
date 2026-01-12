import { FeatureCard } from "@/shared/ui/feature-card";
import { MessageCircle, FolderOpen, FileText, KeyRound } from "lucide-react";

export const HomeFeatureCards = () => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
      <FeatureCard
        icon={<MessageCircle className="h-5 w-5" />}
        title="AI 대화"
        description="AI 챗봇과 대화하며 질문에 대한 답변을 받아보세요."
        to="/chat"
        buttonText="대화 시작하기"
      />

      <FeatureCard
        icon={<FolderOpen className="h-5 w-5" />}
        title="컬렉션 관리"
        description="문서 컬렉션을 생성하고 관리하세요."
        to="/collections"
        buttonText="컬렉션 보기"
      />

      <FeatureCard
        icon={<FileText className="h-5 w-5" />}
        title="문서 관리"
        description="RAG에 사용할 문서를 업로드하고 관리하세요."
        to="/documents"
        buttonText="문서 관리"
      />

      <FeatureCard
        icon={<KeyRound className="h-5 w-5" />}
        title="모델 API 키 관리"
        description="여러 AI 모델의 API 키를 안전하게 관리하세요."
        to="/model-keys"
        buttonText="API 키 관리"
      />
    </div>
  );
};
