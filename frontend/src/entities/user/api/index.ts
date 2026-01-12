import { kyClient } from "@/shared/api/ky-client";
import type {
  LoginCredentials,
  LoginResponse,
  RegisterPayload,
  User,
  ChangePasswordPayload,
  ChangePasswordResponse,
  UpdateProfilePayload,
} from "../types";

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<LoginResponse> => {
    const response = await kyClient.post("auth/login", {
      json: credentials,
    });
    return response.json();
  },

  register: async (payload: RegisterPayload): Promise<User> => {
    const response = await kyClient.post("users", {
      json: payload,
    });
    return response.json();
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await kyClient.get("auth/me");
    return response.json();
  },

  refreshToken: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await kyClient.post("auth/refresh", {
      json: { refresh_token: refreshToken },
    });
    return response.json();
  },

  changePassword: async (
    payload: ChangePasswordPayload
  ): Promise<ChangePasswordResponse> => {
    const response = await kyClient.post("auth/change-password", {
      json: payload,
    });
    return response.json();
  },

  updateProfile: async (payload: UpdateProfilePayload): Promise<User> => {
    const response = await kyClient.patch("users/me", {
      json: payload,
    });
    return response.json();
  },
};
