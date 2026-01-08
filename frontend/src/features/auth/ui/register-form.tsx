import { useState } from "react";
import { Link, useNavigate } from "react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Card, CardHeader, CardTitle, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Label } from "@/shared/ui/label";

import {
  useAuthStore,
  registerSchema,
  type RegisterFormData,
  type RegisterPayload,
} from "@/entities/user";

export const RegisterForm = () => {
  const { register: registerUser } = useAuthStore();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      setIsLoading(true);
      const payload: RegisterPayload = {
        username: data.username,
        password: data.password,
        nickname: data.nickname,
        email: data.email,
      };
      await registerUser(payload);
      navigate("/login");
    } catch (error) {
      console.error("회원가입 실패:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-center">회원가입</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="username">사용자명</Label>
            <Input
              id="username"
              {...register("username")}
              placeholder="사용자명을 입력하세요"
              disabled={isLoading}
            />
            {errors.username && (
              <p className="text-destructive text-sm">{errors.username.message}</p>
            )}
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
              placeholder="이메일을 입력하세요"
              disabled={isLoading}
            />
            {errors.email && (
              <p className="text-destructive text-sm">{errors.email.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="password">비밀번호</Label>
            <Input
              id="password"
              type="password"
              {...register("password")}
              placeholder="비밀번호를 입력하세요"
              disabled={isLoading}
            />
            {errors.password && (
              <p className="text-destructive text-sm">{errors.password.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="confirmPassword">비밀번호 확인</Label>
            <Input
              id="confirmPassword"
              type="password"
              {...register("confirmPassword")}
              placeholder="비밀번호를 다시 입력하세요"
              disabled={isLoading}
            />
            {errors.confirmPassword && (
              <p className="text-destructive text-sm">
                {errors.confirmPassword.message}
              </p>
            )}
          </div>

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "가입 중..." : "회원가입"}
          </Button>
        </form>

        <div className="mt-4 text-center text-sm">
          <span className="text-muted-foreground">이미 계정이 있나요? </span>
          <Link className="text-primary underline-offset-4 hover:underline" to="/login">
            로그인
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};
