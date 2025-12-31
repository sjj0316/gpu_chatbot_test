import { HomeFeatureCards } from "@/widgets/home";

export const HomePage = () => {
  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">BD 챗봇에 오신 것을 환영합니다</h1>
        <p className="text-muted-foreground">
          AI 챗봇과 문서 관리 시스템을 통해 효율적인 작업을 시작하세요.
        </p>
      </div>

      <HomeFeatureCards />
    </div>
  );
};
