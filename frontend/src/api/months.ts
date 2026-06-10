import { api } from './client';
import type { MonthSummary } from './types';

export function getMonthSummary(year: number, month: number): Promise<MonthSummary> {
  return api.get<MonthSummary>(`/months/${year}/${month}`);
}
