import { ProfileForm, ChangePasswordForm } from "@/features/auth";

/**
 * Why: 프로필 편집과 비밀번호 변경을 한 화면에서 제공합니다.
 */
export const ProfilePage = () => {
  return (
    <div className="container mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold">사용자 설정</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          프로필과 비밀번호를 한 곳에서 관리할 수 있습니다.
        </p>
      </div>
      <ProfileForm />
      <ChangePasswordForm />
    </div>
  );
};
