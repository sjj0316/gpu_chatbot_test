import { ReactNode } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/shared/ui/card";
import { Button } from "@/shared/ui/button";
import { Link } from "react-router";

interface FeatureCardProps {
  icon: ReactNode;
  title: string;
  description: string;
  to: string;
  buttonText: string;
}

export const FeatureCard = ({ icon, title, description, to, buttonText }: FeatureCardProps) => {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          {icon}
          {title}
        </CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent>
        <Link to={to}>
          <Button className="w-full">{buttonText}</Button>
        </Link>
      </CardContent>
    </Card>
  );
};
