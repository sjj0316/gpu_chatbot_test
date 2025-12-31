import { useState } from "react";

import { useCollections, type Collection } from "@/entities/collection";
import {
  CollectionsTable,
  CreateCollectionModal,
  EditCollectionModal,
} from "@/features/manage-collection";

import { CollectionsHeader } from "./collections-header";

export const CollectionsManager = () => {
  const { data: collections, isLoading } = useCollections();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [editingCollection, setEditingCollection] = useState<Collection | null>(null);

  return (
    <div className="container mx-auto p-6">
      <CollectionsHeader onCreate={() => setIsCreateModalOpen(true)} />

      <CollectionsTable
        collections={collections?.items ?? []}
        onEdit={setEditingCollection}
        isLoading={isLoading}
      />

      <CreateCollectionModal open={isCreateModalOpen} onOpenChange={setIsCreateModalOpen} />

      {editingCollection && (
        <EditCollectionModal
          collection={editingCollection}
          open={!!editingCollection}
          onOpenChange={(open) => !open && setEditingCollection(null)}
        />
      )}
    </div>
  );
};
