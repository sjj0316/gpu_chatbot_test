import { Link } from "react-router";
import { Info, MessageCircle, FolderOpen, FileText, KeyRound, Settings, User } from "lucide-react";

import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/ui/tooltip";

type UsageCard = {
  title: string;
  description: string;
  detail: string;
  to: string;
  icon: React.ReactNode;
};

const cards: UsageCard[] = [
  {
    title: "대화하기",
    description: "모델 키를 선택하고 대화를 시작하세요.",
    detail: "대화 생성 시 기본 API 키를 지정하면 이후 기본값으로 유지됩니다.",
    to: "/chat",
    icon: <MessageCircle className="h-5 w-5" />,
  },
  {
    title: "컬렉션 관리",
    description: "문서를 묶을 컬렉션을 만들고 관리합니다.",
    detail: "문서 업로드 전 반드시 컬렉션을 선택해야 합니다.",
    to: "/collections",
    icon: <FolderOpen className="h-5 w-5" />,
  },
  {
    title: "문서 관리",
    description: "문서를 업로드하고 청크 설정을 조정합니다.",
    detail: "청크 크기/오버랩은 검색 품질에 큰 영향을 줍니다.",
    to: "/documents",
    icon: <FileText className="h-5 w-5" />,
  },
  {
    title: "모델 키 관리",
    description: "API 키를 등록/수정/비활성화합니다.",
    detail: "용도(채팅/임베딩)에 맞는 키를 선택하세요.",
    to: "/model-keys",
    icon: <KeyRound className="h-5 w-5" />,
  },
  {
    title: "MCP 서버",
    description: "외부 도구/서버를 연결해 확장 기능을 사용합니다.",
    detail: "서버 접근 권한은 관리자 정책에 따라 제한될 수 있습니다.",
    to: "/mcp-servers",
    icon: <Settings className="h-5 w-5" />,
  },
  {
    title: "프로필/보안",
    description: "닉네임, 이메일, 비밀번호를 관리합니다.",
    detail: "비밀번호 변경은 현재 비밀번호 확인 후 가능합니다.",
    to: "/profile",
    icon: <User className="h-5 w-5" />,
  },
];

const UsageCardItem = ({ card }: { card: UsageCard }) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {card.icon}
          <span>{card.title}</span>
          <Tooltip>
            <TooltipTrigger asChild>
              <span className="text-muted-foreground inline-flex cursor-help items-center">
                <Info className="h-3.5 w-3.5" />
              </span>
            </TooltipTrigger>
            <TooltipContent side="top">{card.detail}</TooltipContent>
          </Tooltip>
        </CardTitle>
        <CardDescription>{card.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Link to={card.to}>
          <Button className="w-full">자세히 보기</Button>
        </Link>
      </CardContent>
    </Card>
  );
};

export const HomeUsageCards = () => {
  return (
    <div className="grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-3">
      {cards.map((card) => (
        <UsageCardItem key={card.title} card={card} />
      ))}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            전체 사용 가이드
          </CardTitle>
          <CardDescription>위키 형식의 문서로 전체 기능을 확인하세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <Link to="/guide">
            <Button className="w-full" variant="secondary">
              가이드 열기
            </Button>
          </Link>
        </CardContent>
      </Card>
    </div>
  );
};
