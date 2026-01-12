import React, { lazy, Suspense } from "react";
import { createBrowserRouter, RouterProvider, Navigate } from "react-router";

import { RootLayout } from "@/widgets/layout";
import { useAuthStore } from "@/entities/user";
import { ComponentLoading } from "@/shared/ui/component-loading";

const HomePage = lazy(() =>
  import("@/pages/home").then((module) => ({
    default: module.HomePage,
  }))
);
const AboutPage = lazy(() =>
  import("@/pages/about").then((module) => ({
    default: module.AboutPage,
  }))
);
const ChatPage = lazy(() =>
  import("@/pages/chat").then((module) => ({
    default: module.ChatPage,
  }))
);
const CollectionsPage = lazy(() =>
  import("@/pages/collection").then((module) => ({
    default: module.CollectionsPage,
  }))
);
const DocumentsPage = lazy(() =>
  import("@/pages/document").then((module) => ({
    default: module.DocumentsPage,
  }))
);
const DocumentSearchPage = lazy(() =>
  import("@/pages/document").then((module) => ({
    default: module.DocumentSearchPage,
  }))
);
const ModelKeysPage = lazy(() =>
  import("@/pages/model-key").then((module) => ({
    default: module.ModelKeysPage,
  }))
);

const NotFoundPage = lazy(() =>
  import("@/pages/error").then((module) => ({
    default: module.NotFoundPage,
  }))
);
const LoginPage = lazy(() =>
  import("@/pages/auth").then((module) => ({
    default: module.LoginPage,
  }))
);
const RegisterPage = lazy(() =>
  import("@/pages/auth").then((module) => ({
    default: module.RegisterPage,
  }))
);
const ChangePasswordPage = lazy(() =>
  import("@/pages/auth").then((module) => ({
    default: module.ChangePasswordPage,
  }))
);
const ProfilePage = lazy(() =>
  import("@/pages/profile").then((module) => ({
    default: module.ProfilePage,
  }))
);
const MCPServerPage = lazy(() =>
  import("@/pages/mcp-server").then((module) => ({
    default: module.MCPServerPage,
  }))
);
const GuidePage = lazy(() =>
  import("@/pages/guide").then((module) => ({
    default: module.GuidePage,
  }))
);

// 보호된 라우트들
const protectedRoutesConfig = [
  {
    path: "/",
    index: true,
    element: <HomePage />,
  },
  {
    path: "about",
    element: <AboutPage />,
  },
  {
    path: "chat",
    element: <ChatPage />,
  },
  {
    path: "collections",
    element: <CollectionsPage />,
  },
  {
    path: "documents",
    element: <DocumentsPage />,
  },
  {
    path: "search",
    element: <DocumentSearchPage />,
  },
  {
    path: "model-keys",
    element: <ModelKeysPage />,
  },
  {
    path: "mcp-servers",
    element: <MCPServerPage />,
  },
  {
    path: "change-password",
    element: <ChangePasswordPage />,
  },
  {
    path: "profile",
    element: <ProfilePage />,
  },
  {
    path: "guide",
    element: <GuidePage />,
  },
];

// 보호된 라우터 래퍼
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated, isLoading, getCurrentUser } = useAuthStore();

  React.useEffect(() => {
    getCurrentUser();
  }, [getCurrentUser]);

  if (isLoading) {
    return <ComponentLoading />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// 라우터 생성
const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <Suspense fallback={<ComponentLoading />}>
        <LoginPage />
      </Suspense>
    ),
  },
  {
    path: "/register",
    element: (
      <Suspense fallback={<ComponentLoading />}>
        <RegisterPage />
      </Suspense>
    ),
  },
  {
    path: "/",
    element: (
      <ProtectedRoute>
        <RootLayout />
      </ProtectedRoute>
    ),
    // element: <RootLayout />,
    children: protectedRoutesConfig
      .map(({ path, index, element }) =>
        index
          ? {
              index: true,
              element: <Suspense fallback={<ComponentLoading />}>{element}</Suspense>,
            }
          : {
              path,
              element: <Suspense fallback={<ComponentLoading />}>{element}</Suspense>,
            }
      )
      .concat([
        {
          path: "*",
          element: (
            <Suspense fallback={<ComponentLoading />}>
              <NotFoundPage />
            </Suspense>
          ),
        },
      ]),
  },
]);

export const AppRouter = () => {
  return <RouterProvider router={router} />;
};
