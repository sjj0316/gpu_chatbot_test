import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, "사용자명을 입력해주세요"),
  password: z.string().min(1, "비밀번호를 입력해주세요"),
});

export const registerSchema = z
  .object({
    username: z.string().min(1, "사용자명을 입력해주세요"),
    password: z.string().min(8, "비밀번호는 최소 8자 이상 입력해주세요"),
    confirmPassword: z
      .string()
      .min(8, "비밀번호 확인을 입력해주세요"),
    nickname: z.string().min(1, "닉네임을 입력해주세요"),
    email: z.string().email("유효한 이메일을 입력해주세요"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    path: ["confirmPassword"],
    message: "비밀번호가 일치하지 않습니다",
  });

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, "현재 비밀번호를 입력해주세요"),
    new_password: z.string().min(8, "새 비밀번호는 최소 8자 이상 입력해주세요"),
    confirm_password: z.string().min(1, "새 비밀번호를 다시 입력해주세요"),
  })
  .refine((data) => data.new_password === data.confirm_password, {
    path: ["confirm_password"],
    message: "새 비밀번호가 일치하지 않습니다",
  });

export const profileSchema = z.object({
  nickname: z.string().min(1, "닉네임을 입력해주세요"),
  email: z.string().email("이메일 형식이 올바르지 않습니다"),
});

export const userSchema = z.object({
  id: z.number(),
  username: z.string(),
  nickname: z.string(),
  email: z.string().email(),
});

export const loginResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
});

export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type ChangePasswordFormData = z.infer<typeof changePasswordSchema>;
export type ProfileFormData = z.infer<typeof profileSchema>;
export type UserData = z.infer<typeof userSchema>;
export type LoginResponseData = z.infer<typeof loginResponseSchema>;
