import { Card, CardContent } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";
import type { DocumentsSearchResponseItem } from "../model";

interface SearchResultCardProps {
  result: DocumentsSearchResponseItem;
}

export const SearchResultCard = ({ result }: SearchResultCardProps) => {
  const getSourceFileName = () => {
    if (result.metadata?.source) {
      return result.metadata.source;
    }
    return "알 수 없는 소스";
  };

  return (
    <Card className="transition-shadow hover:shadow-md">
      <CardContent className="pt-4">
        <div className="mb-2 flex items-center justify-between">
          <h4 className="truncate font-medium">{getSourceFileName()}</h4>
          <Badge variant="secondary">점수: {result.score && result.score.toFixed(4)}</Badge>
        </div>
        <p className="text-muted-foreground line-clamp-3 text-sm">{result.page_content}</p>
        {result.metadata && Object.keys(result.metadata).length > 0 && (
          <div className="mt-2 flex flex-wrap gap-1">
            {Object.entries(result.metadata)
              .slice(0, 3)
              .map(([key, value]) => (
                <Badge key={key} variant="outline" className="text-xs">
                  {key}: {String(value)}
                </Badge>
              ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
