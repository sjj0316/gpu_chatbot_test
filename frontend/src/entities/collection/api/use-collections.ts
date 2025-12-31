import { useQuery } from "@tanstack/react-query";

import { collectionQueries } from "./collection.queries";
import type { CollectionsListParams } from "../model";

export const useCollections = (params?: CollectionsListParams) => {
  return useQuery(collectionQueries.list(params));
};
