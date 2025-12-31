import { useQuery } from "@tanstack/react-query";

import { modelKeyQueries } from "./model-key.queries";
import {  type AiModelKeysListParams } from "../model";

export const useModelKeys = (params?: AiModelKeysListParams) => {
  return useQuery(modelKeyQueries.list(params));
};
