import { Database } from "lucide-react";

import { Tabs, TabsList, TabsTrigger } from "@/shared/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";

import type { DocumentViewType } from "../model";

type DocumentTopbarBaseProps = {
  activeTab: DocumentViewType;
  totalCount: number;
  limit: number;
  onTabChange: (tab: DocumentViewType) => void;
  onLimitChange: (limit: number) => void;
};

export const DocumentTopbarBase = ({
  activeTab,
  totalCount,
  limit,
  onTabChange,
  onLimitChange,
}: DocumentTopbarBaseProps) => {
  return (
    <div className="mb-4 flex items-center justify-between">
      <Tabs value={activeTab} onValueChange={(v) => onTabChange(v as DocumentViewType)}>
        <TabsList>
          <TabsTrigger value="document">문서</TabsTrigger>
          <TabsTrigger value="chunk">청크</TabsTrigger>
        </TabsList>
      </Tabs>

      <div className="flex items-center gap-4">
        <div className="text-muted-foreground flex items-center gap-2 text-sm">
          <Database className="h-4 w-4" />
          <span>
            전체 {activeTab === "document" ? "문서" : "청크"}: {totalCount}
          </span>
        </div>

        <Select value={String(limit)} onValueChange={(v) => onLimitChange(parseInt(v))}>
          <SelectTrigger className="w-32">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="10">10개씩</SelectItem>
            <SelectItem value="20">20개씩</SelectItem>
            <SelectItem value="50">50개씩</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  );
};
