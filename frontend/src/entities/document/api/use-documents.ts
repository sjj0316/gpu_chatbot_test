import { useQuery } from "@tanstack/react-query";

import { documentQueries } from "./document.queries";
import { type DocumentsListParams } from "../model";

export const useDocuments = (collectionId: string, params?: DocumentsListParams) => {
  return useQuery({ ...documentQueries.list(collectionId, params), enabled: !!collectionId });
};
