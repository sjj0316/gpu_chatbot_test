import { Outlet } from "react-router";
import { SidebarProvider, SidebarInset } from "@/shared/ui/sidebar";

import { AppHeader } from "./app-header";
import { AppSidebar } from "./app-sidebar";
import { AppFooter } from "./app-footer";

export const RootLayout = () => {
  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full">
        <AppSidebar />

        <SidebarInset className="flex-1">
          <AppHeader />

          <main className="flex-1 overflow-auto pt-16 pb-12">
            <Outlet />
          </main>

          <AppFooter />
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};
