export {
  collectionQueries,
  useCollections,
  useCreateCollection,
  useDeleteCollection,
  useUpdateCollection,
} from "./api";

export {
  collectionSchema,
  createCollectionSchema,
  updateCollectionSchema,
  collectionsListResponseSchema,
  collectionsListParamsSchema,
  type Collection,
  type CreateCollectionRequest,
  type UpdateCollectionRequest,
  type CreateCollectionResponse,
  type CollectionsListResponse,
  type CollectionsListParams,
} from "./model";

export { CollectionSelectBase, CollectionsTableBase, CollectionDeleteDialog } from "./ui";
