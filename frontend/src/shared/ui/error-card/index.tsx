import { ReactNode } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/shared/ui/card";

interface ErrorCardProps {
  code?: string;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}

export const ErrorCard = ({ code, title, description, action, className = "" }: ErrorCardProps) => {
  return (
    <Card className={`max-w-md text-center ${className}`}>
      <CardHeader>
        {code && (
          <CardTitle className="mb-4 text-6xl font-bold text-muted-foreground">{code}</CardTitle>
        )}
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {description && <p className="mb-6 text-muted-foreground">{description}</p>}
        {action}
      </CardContent>
    </Card>
  );
};
