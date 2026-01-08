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
export type UserData = z.infer<typeof userSchema>;
export type LoginResponseData = z.infer<typeof loginResponseSchema>;
