import { useState } from "react";

import { useModelKeys } from "@/entities/model-key";
import {
  ModelKeysTable,
  CreateModelKeyModal,
  EditModelKeyModal,
} from "@/features/manage-model-key";
import type { ModelApiKeyRead, AiModelKeysListParams } from "@/entities/model-key";

import { ModelKeysHeader } from "./model-keys-header";

export const ModelKeysManager = () => {
  const [filters, setFilters] = useState<AiModelKeysListParams>({ include_public: true });
  const { data, isLoading } = useModelKeys(filters);

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingRow, setEditingRow] = useState<ModelApiKeyRead | null>(null);

  return (
    <div className="container mx-auto p-6">
      <ModelKeysHeader
        onCreate={() => setIsCreateOpen(true)}
        filters={filters}
        onChangeFilters={setFilters}
      />

      <ModelKeysTable rows={data ?? []} isLoading={isLoading} onEdit={setEditingRow} />

      <CreateModelKeyModal open={isCreateOpen} onOpenChange={setIsCreateOpen} />

      {editingRow && (
        <EditModelKeyModal
          row={editingRow}
          open={!!editingRow}
          onOpenChange={(open) => !open && setEditingRow(null)}
        />
      )}
    </div>
  );
};
