import { useState } from "react";

import { UploadDocumentModal, DocumentListView } from "@/features/manage-document";
import { DocumentHeader } from "./document-header";

export const DocumentManager = () => {
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string>("");

  return (
    <div className="container mx-auto p-6">
      <DocumentHeader
        onUpload={() => setIsUploadModalOpen(true)}
        collectionId={selectedCollectionId}
        onChangeCollectionId={setSelectedCollectionId}
      />

      <DocumentListView collectionId={selectedCollectionId} />

      <UploadDocumentModal
        isOpen={isUploadModalOpen}
        onOpenChange={setIsUploadModalOpen}
        collectionId={selectedCollectionId}
      />
    </div>
  );
};
