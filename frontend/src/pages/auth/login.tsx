import { useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuthStore } from "@/entities/user";
import { LoginForm } from "@/features/auth";

/**
 * Why: 사용자가 계정 인증을 시작할 수 있는 진입점입니다.
 *
 * Contract:
 * - 이미 인증된 경우 홈으로 리다이렉트합니다.
 */
export const LoginPage = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="container mx-auto max-w-md p-6">
      <LoginForm />
    </div>
  );
};
