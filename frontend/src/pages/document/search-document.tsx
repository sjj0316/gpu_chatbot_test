import { useState } from "react";
import { Search, Database } from "lucide-react";

import { Button } from "@/shared/ui/button";
import { Input } from "@/shared/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/ui/card";
import { Badge } from "@/shared/ui/badge";

import { useCollections } from "@/entities/collection";
import { useSearchDocument, SearchResultCard, type DocumentSearchType } from "@/entities/document";
import { ModelKeySelect } from "@/entities/model-key";

/**
 * Why: 컬렉션 내 문서를 검색하고 결과를 요약해 보여줍니다.
 *
 * Contract:
 * - 컬렉션 선택과 검색어 입력이 있어야 검색이 실행됩니다.
 */
export const DocumentSearchPage = () => {
  const [query, setQuery] = useState("");
  const [selectedCollectionId, setSelectedCollectionId] = useState<string>("");
  const [searchType, setSearchType] = useState<DocumentSearchType>("semantic");
  const [limit, setLimit] = useState(10);
  const [modelKeyId, setModelKeyId] = useState<string | null>(null);

  const { data: collectionsData } = useCollections();
  const collections = collectionsData?.items || [];

  const { data: searchResults, isPending: isLoading, mutate: performSearch } = useSearchDocument();

  const handleSearch = () => {
    if (!selectedCollectionId || !query.trim()) return;

    // 선택된 모델 키가 있으면 요청에 포함
    const requestPayload: any = {
      query: query.trim(),
      limit,
      search_type: searchType,
      filter: {},
    };
    if (modelKeyId) {
      requestPayload.model_api_key_id = modelKeyId;
    }

    performSearch({
      collectionId: selectedCollectionId,
      request: requestPayload,
    });
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold">문서 검색</h1>
        <p className="text-muted-foreground">
          컬렉션 내에서 벡터 검색을 수행하여 관련 문서를 찾아보세요.
        </p>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            검색 설정
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 기존 2열 → 모델 키 추가를 위해 3열로 변경 */}
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="space-y-2">
              <label className="text-sm font-medium">컬렉션 선택</label>
              <Select value={selectedCollectionId} onValueChange={setSelectedCollectionId}>
                <SelectTrigger>
                  <SelectValue placeholder="검색할 컬렉션을 선택하세요" />
                </SelectTrigger>
                <SelectContent>
                  {collections.map((collection) => (
                    <SelectItem key={collection.collection_id} value={collection.collection_id}>
                      <div className="flex w-full items-center justify-between">
                        <span>
                          {collection.name} - {collection.embedding_model}
                        </span>
                        <Badge variant="secondary" className="ml-2">
                          {collection.document_count}개 문서
                        </Badge>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">검색 타입</label>
              <Select
                value={searchType}
                onValueChange={(value) => setSearchType(value as DocumentSearchType)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="semantic">의미 검색 (Semantic)</SelectItem>
                  <SelectItem value="keyword">키워드 검색 (Keyword)</SelectItem>
                  <SelectItem value="hybrid">하이브리드 검색 (Hybrid)</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* 추가: 모델 키 선택 */}
            <div className="space-y-2">
              <label className="text-sm font-medium">모델 키 (선택)</label>
              <ModelKeySelect
                value={modelKeyId}
                onChange={setModelKeyId}
                placeholder="모델 키를 선택하세요"
                // 필요시 필터링/제한 조건 props를 여기에 전달 (예: purpose='embedding' 등)
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">검색어</label>
            <div className="flex gap-2">
              <Input
                placeholder="검색할 내용을 입력하세요..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
              />
              <Select value={limit.toString()} onValueChange={(value) => setLimit(parseInt(value))}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5개</SelectItem>
                  <SelectItem value="10">10개</SelectItem>
                  <SelectItem value="20">20개</SelectItem>
                  <SelectItem value="50">50개</SelectItem>
                </SelectContent>
              </Select>
              <Button
                onClick={handleSearch}
                disabled={!selectedCollectionId || !query.trim() || isLoading}
              >
                <Search className="mr-2 h-4 w-4" />
                검색
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {searchResults && searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="text-muted-foreground flex items-center gap-2 text-sm">
            <Database className="h-4 w-4" />
            <span>{searchResults.length}개의 검색 결과</span>
          </div>

          <div className="space-y-4">
            {searchResults.map((result, index) => (
              <SearchResultCard key={`${result.id}-${index}`} result={result} />
            ))}
          </div>
        </div>
      )}

      {searchResults && searchResults.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <Search className="text-muted-foreground mb-4 h-12 w-12" />
            <CardTitle className="mb-2">검색 결과가 없습니다</CardTitle>
            <CardDescription>다른 검색어를 시도해보세요.</CardDescription>
          </CardContent>
        </Card>
      )}

      {!searchResults && !isLoading && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-8">
            <Search className="text-muted-foreground mb-4 h-12 w-12" />
            <CardTitle className="mb-2">검색을 시작하세요</CardTitle>
            <CardDescription>
              컬렉션을 선택하고 검색어를 입력한 후 검색 버튼을 클릭하세요.
            </CardDescription>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
