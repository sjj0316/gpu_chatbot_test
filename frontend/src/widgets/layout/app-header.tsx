import { Link, useNavigate } from "react-router";
import { User, LogOut } from "lucide-react";

import { Button } from "@/shared/ui/button";
import { ModeToggle } from "@/shared/ui/mode-toggle";
import { SidebarTrigger } from "@/shared/ui/sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/shared/ui/dropdown-menu";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/shared/ui/alert-dialog";

import { useAuthStore } from "@/entities/user";

export const AppHeader = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  return (
    <header className="border-border bg-background fixed top-0 right-0 left-0 z-50 flex h-16 items-center justify-between border-b px-4">
      <div className="flex items-center gap-3">
        <SidebarTrigger />
        <Link to="/" className="text-primary text-xl font-bold">
          BD 챗봇
        </Link>
      </div>

      <div className="flex items-center gap-2">
        <ModeToggle />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="sm">
              <User className="h-4 w-4" />
              <span className="ml-2">{user?.nickname || "사용자"}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <DropdownMenuItem onSelect={() => navigate("/profile")}>
              사용자 설정
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
        <AlertDialog>
          <AlertDialogTrigger asChild>
            <Button className="cursor-pointer" variant="ghost" size="icon" title="로그아웃">
              <LogOut className="h-4 w-4" />
            </Button>
          </AlertDialogTrigger>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>로그아웃 확인</AlertDialogTitle>
              <AlertDialogDescription>
                정말 로그아웃 하시겠습니까?
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>취소</AlertDialogCancel>
              <AlertDialogAction onClick={logout}>로그아웃</AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </header>
  );
};
