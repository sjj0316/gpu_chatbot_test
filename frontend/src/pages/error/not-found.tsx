import { ErrorCard } from "@/shared/ui/error-card";
import { Button } from "@/shared/ui/button";
import { Home } from "lucide-react";
import { Link } from "react-router";

export const NotFoundPage = () => {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <ErrorCard
        code="404"
        title="페이지를 찾을 수 없습니다"
        description="요청하신 페이지가 존재하지 않거나 이동되었습니다."
        action={
          <Link to="/">
            <Button>
              <Home className="mr-2 h-4 w-4" />
              홈으로 돌아가기
            </Button>
          </Link>
        }
      />
    </div>
  );
};
