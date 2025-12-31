import { ReactNode } from "react";

import { TooltipProvider } from "@/shared/ui/tooltip";
import { Toaster } from "@/shared/ui/sonner";

import { ReactQueryProvider } from "./react-query-provider";
import { ThemeProvider } from "./theme-provider";

interface AppProvidersProps {
  children: ReactNode;
}

export const AppProviders = ({ children }: AppProvidersProps) => (
  <ReactQueryProvider>
    <ThemeProvider>
      <TooltipProvider>
        <Toaster position="top-center" />
        {children}
      </TooltipProvider>
    </ThemeProvider>
  </ReactQueryProvider>
);
