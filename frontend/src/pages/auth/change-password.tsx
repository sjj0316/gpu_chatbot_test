import { ChangePasswordForm } from "@/features/auth";

/**
 * Why: 사용자가 비밀번호를 단독으로 변경할 수 있게 합니다.
 */
export const ChangePasswordPage = () => {
  return (
    <div className="container mx-auto max-w-md p-6">
      <ChangePasswordForm />
    </div>
  );
};
