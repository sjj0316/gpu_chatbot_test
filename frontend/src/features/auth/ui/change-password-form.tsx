import { useState } from "react";
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
  changePasswordSchema,
  type ChangePasswordFormData,
  type ChangePasswordPayload,
} from "@/entities/user";

export const ChangePasswordForm = () => {
  const { changePassword } = useAuthStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ChangePasswordFormData>({
    resolver: zodResolver(changePasswordSchema),
  });

  const onSubmit = async (data: ChangePasswordFormData) => {
    try {
      setIsLoading(true);
      const payload: ChangePasswordPayload = {
        current_password: data.current_password,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      };
      await changePassword(payload);
      toast.success("비밀번호 변경 완료", {
        description: "비밀번호가 변경되었습니다.",
      });
      reset();
    } catch (error) {
      const message = await getApiErrorMessage(error, "변경에 실패했습니다.");
      toast.error("비밀번호 변경 실패", { description: message });
      console.error("Change password failed:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">비밀번호 변경</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="current_password">현재 비밀번호</Label>
            <Input
              id="current_password"
              type="password"
              {...register("current_password")}
              placeholder="현재 비밀번호를 입력하세요"
              disabled={isLoading}
            />
            {errors.current_password && (
              <p className="text-destructive text-sm">
                {errors.current_password.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="new_password">새 비밀번호</Label>
            <Input
              id="new_password"
              type="password"
              {...register("new_password")}
              placeholder="새 비밀번호를 입력하세요"
              disabled={isLoading}
            />
            {errors.new_password && (
              <p className="text-destructive text-sm">
                {errors.new_password.message}
              </p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirm_password">새 비밀번호 확인</Label>
            <Input
              id="confirm_password"
              type="password"
              {...register("confirm_password")}
              placeholder="새 비밀번호를 다시 입력하세요"
              disabled={isLoading}
            />
            {errors.confirm_password && (
              <p className="text-destructive text-sm">
                {errors.confirm_password.message}
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "변경 중..." : "비밀번호 변경"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
};
