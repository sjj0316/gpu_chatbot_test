import { HomeFeatureCards, HomeUsageCards } from "@/widgets/home";

export const HomePage = () => {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">BD 챗봇에 오신 것을 환영합니다</h1>
        <p className="text-muted-foreground">
          AI 챗봇과 문서 관리 기능을 통해 업무 효율을 높이세요.
        </p>
      </div>

      <HomeFeatureCards />

      <div className="mt-10">
        <h2 className="mb-3 text-2xl font-semibold">사용 가이드</h2>
        <p className="text-muted-foreground mb-6">
          각 기능별 핵심 흐름과 주의사항을 확인하세요. 카드에 마우스를 올리면 상세 설명이
          표시됩니다.
        </p>
        <HomeUsageCards />
      </div>
    </div>
  );
};
