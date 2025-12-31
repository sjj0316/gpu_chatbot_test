import { z } from "zod";

export const loginSchema = z.object({
  username: z.string().min(1, "사용자명을 입력해주세요"),
  password: z.string().min(1, "비밀번호를 입력해주세요"),
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
export type UserData = z.infer<typeof userSchema>;
export type LoginResponseData = z.infer<typeof loginResponseSchema>;
