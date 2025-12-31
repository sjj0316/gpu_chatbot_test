import { Loader2 } from "lucide-react";

export const ComponentLoading = () => {
  return (
    <div className="flex h-[200px] w-full items-center justify-center">
      <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
    </div>
  );
};
