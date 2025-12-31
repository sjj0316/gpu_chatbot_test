import { useMemo, useState } from "react";

import { Spinner } from "@/shared/ui/spinner";
import { FooterPagination } from "@/shared/ui/pagination";
import {
  useDocuments,
  DocumentDetailDialog,
  DocumentChunkDetailDialog,
  DocumentTopbarBase,
  type DocumentFile,
  type ChunkItem,
  type DocumentViewType,
} from "@/entities/document";

import { DocumentsTable } from "./documents-table";
import { ChunksTable } from "./chunks-table";

type DocumentListViewProps = {
  collectionId: string;
};

export const DocumentListView = ({ collectionId }: DocumentListViewProps) => {
  const [activeTab, setActiveTab] = useState<DocumentViewType>("document");
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);

  const [selectedDocument, setSelectedDocument] = useState<DocumentFile | null>(null);
  const [selectedChunk, setSelectedChunk] = useState<ChunkItem | null>(null);

  const offset = (page - 1) * limit;
  const params = useMemo(() => ({ limit, offset, view: activeTab }), [limit, offset, activeTab]);

  const { data, isLoading } = useDocuments(collectionId, params);

  const items = data?.items ?? [];
  const totalCount =
    activeTab === "document" ? ((data as any)?.file_total ?? 0) : ((data as any)?.chunk_total ?? 0);

  const handleTabChange = (t: DocumentViewType) => {
    setActiveTab(t);
    setPage(1);
  };

  const handleLimitChange = (l: number) => {
    setLimit(l);
    setPage(1);
  };

  return (
    <>
      <DocumentTopbarBase
        activeTab={activeTab}
        totalCount={totalCount}
        limit={limit}
        onTabChange={handleTabChange}
        onLimitChange={handleLimitChange}
      />

      {isLoading ? (
        <div className="flex h-64 items-center justify-center">
          <Spinner size="lg" />
        </div>
      ) : activeTab === "document" ? (
        <DocumentsTable
          documents={items}
          collectionId={collectionId}
          onDocumentClick={setSelectedDocument}
        />
      ) : (
        <ChunksTable chunks={items} collectionId={collectionId} onChunkClick={setSelectedChunk} />
      )}

      <FooterPagination page={page} limit={limit} totalCount={totalCount} onPageChange={setPage} />
      {/* 상세 다이얼로그들 */}
      {selectedDocument && (
        <DocumentDetailDialog
          document={selectedDocument}
          isOpen={!!selectedDocument}
          onOpenChange={(open) => !open && setSelectedDocument(null)}
        />
      )}

      {selectedChunk && (
        <DocumentChunkDetailDialog
          chunk={selectedChunk}
          isOpen={!!selectedChunk}
          onOpenChange={(open) => !open && setSelectedChunk(null)}
        />
      )}
    </>
  );
};
