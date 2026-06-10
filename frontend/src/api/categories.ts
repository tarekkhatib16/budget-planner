import { api } from './client';
import type { Category, CategoryGroup } from './types';

export function createCategory(payload: {
  name: string;
  group: CategoryGroup;
  sort_order?: number;
}): Promise<Category> {
  return api.post<Category>('/categories', payload);
}

export function deleteCategory(categoryId: number): Promise<void> {
  return api.delete(`/categories/${categoryId}`);
}
