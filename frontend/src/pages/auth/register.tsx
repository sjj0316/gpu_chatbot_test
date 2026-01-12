import { useEffect } from "react";
import { useNavigate } from "react-router";
import { useAuthStore } from "@/entities/user";
import { RegisterForm } from "@/features/auth";

export const RegisterPage = () => {
  const { isAuthenticated } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/");
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="container mx-auto max-w-md p-6">
      <RegisterForm />
    </div>
  );
};
