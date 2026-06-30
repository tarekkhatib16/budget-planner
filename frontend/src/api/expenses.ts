import { api } from './client';
import type { Expense, ExpenseKind } from './types';

export interface ExpenseCreate {
  spend_date: string;
  amount_pence: number;
  description?: string | null;
  kind?: ExpenseKind;
}

export function listExpenses(
  year: number,
  month: number,
  kind: ExpenseKind = 'regular',
): Promise<Expense[]> {
  return api.get<Expense[]>(`/expenses?year=${year}&month=${month}&kind=${kind}`);
}

export function createExpense(payload: ExpenseCreate): Promise<Expense> {
  return api.post<Expense>('/expenses', payload);
}

export function deleteExpense(expenseId: number): Promise<void> {
  return api.delete(`/expenses/${expenseId}`);
}
