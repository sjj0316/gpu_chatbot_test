import { create } from "zustand";
import {
  authApi,
  type LoginCredentials,
  type RegisterPayload,
  type User,
  type AuthState,
} from "../";

interface AuthStore extends AuthState {
  login: (credentials: LoginCredentials) => Promise<any>;
  register: (payload: RegisterPayload) => Promise<User>;
  logout: () => void;
  getCurrentUser: () => Promise<void>;
}

export const useAuthStore = create<AuthStore>((set, get) => ({
  user: null,
  isLoading: true,
  isAuthenticated: false,

  login: async (credentials: LoginCredentials) => {
    try {
      const response = await authApi.login(credentials);
      localStorage.setItem("authToken", response.access_token);
      localStorage.setItem("refreshToken", response.refresh_token);

      // 사용자 정보 조회
      const userData = await authApi.getCurrentUser();
      set({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      });

      return response;
    } catch (error) {
      set({ isAuthenticated: false, isLoading: false });
      throw error;
    }
  },

  register: async (payload: RegisterPayload) => {
    const user = await authApi.register(payload);
    return user;
  },

  logout: () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("refreshToken");
    set({
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  getCurrentUser: async () => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }

    try {
      const userData = await authApi.getCurrentUser();
      set({
        user: userData,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch (error) {
      localStorage.removeItem("authToken");
      localStorage.removeItem("refreshToken");
      set({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
