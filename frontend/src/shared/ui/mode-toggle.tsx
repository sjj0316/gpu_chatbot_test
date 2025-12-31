import { Moon, Sun } from "lucide-react";

import { useTheme } from "@/shared/ui/theme";
import { Switch } from "@/shared/ui/switch";
import { cn } from "@/shared/lib/utils";

type ModeToggleProps = {
  className?: string;
  iconClassName?: string;
};

export function ModeToggle({ className, iconClassName }: ModeToggleProps) {
  const { theme, setTheme } = useTheme();
  const isDark = theme === "dark";

  const handleToggle = () => {
    setTheme(isDark ? "light" : "dark");
  };

  return (
    <Switch
      checked={isDark}
      onCheckedChange={handleToggle}
      className={cn("cursor-pointer data-[state=checked]:bg-zinc-700", className)}
      icon={
        isDark ? (
          <Moon className={cn("h-5 w-5", iconClassName)} />
        ) : (
          <Sun className={cn("h-5 w-5", iconClassName)} />
        )
      }
    />
  );
}
