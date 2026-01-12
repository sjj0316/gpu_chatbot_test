import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";

import { Card, CardHeader, CardTitle, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";
import { getApiErrorMessage } from "@/shared/api/error";

import {
  useAuthStore,
  profileSchema,
  type ProfileFormData,
  type UpdateProfilePayload,
} from "@/entities/user";

export const ProfileForm = () => {
  const { user, updateProfile } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      nickname: user?.nickname || "",
      email: user?.email || "",
    },
  });

  useEffect(() => {
    if (user) {
      reset({
        nickname: user.nickname,
        email: user.email,
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: ProfileFormData) => {
    try {
      setIsLoading(true);
      const payload: UpdateProfilePayload = {
        nickname: data.nickname,
        email: data.email,
      };
      await updateProfile(payload);
      toast.success("프로필 저장", {
        description: "프로필이 저장되었습니다.",
      });
    } catch (error) {
      const message = await getApiErrorMessage(error, "저장에 실패했습니다.");
      toast.error("프로필 저장 실패", { description: message });
      console.error("Profile update failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">프로필</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">아이디</Label>
            <Input id="username" value={user?.username || ""} disabled />
            <p className="text-muted-foreground text-xs">
              아이디 변경은 현재 지원하지 않습니다.
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="nickname">닉네임</Label>
            <Input
              id="nickname"
              {...register("nickname")}
              placeholder="닉네임을 입력하세요"
              disabled={isLoading}
            />
            {errors.nickname && (
              <p className="text-destructive text-sm">{errors.nickname.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="email">이메일</Label>
            <Input
              id="email"
              type="email"
              {...register("email")}
              placeholder="you@example.com"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="text-destructive text-sm">{errors.email.message}</p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "저장 중..." : "저장"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
