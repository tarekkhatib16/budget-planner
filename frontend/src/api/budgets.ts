import { api } from './client';
import type { YearView } from './types';

export function getYearView(year: number): Promise<YearView> {
  return api.get<YearView>(`/budgets/${year}`);
}

export function setBudgetCell(
  year: number,
  month: number,
  categoryId: number,
  amountPence: number,
): Promise<unknown> {
  return api.put(`/budgets/${year}/${month}/categories/${categoryId}`, {
    amount_pence: amountPence,
  });
}

export function copyForward(year: number, month: number): Promise<{ months_filled: number }> {
  return api.post<{ months_filled: number }>(`/budgets/${year}/${month}/copy-forward`, {});
}
