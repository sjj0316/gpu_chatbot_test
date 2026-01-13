import { useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuthStore } from "@/entities/user";
import { RegisterForm } from "@/features/auth";

/**
 * Why: 신규 사용자가 계정을 생성할 수 있도록 합니다.
 *
 * Contract:
 * - 이미 인증된 경우 홈으로 리다이렉트합니다.
 */
export const RegisterPage = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="container mx-auto max-w-md p-6">
      <RegisterForm />
    </div>
  );
};
