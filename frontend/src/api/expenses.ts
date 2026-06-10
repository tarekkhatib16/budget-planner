import { api } from './client';
import type { Expense } from './types';

export interface ExpenseCreate {
  spend_date: string;
  amount_pence: number;
  description?: string | null;
}

export function createExpense(payload: ExpenseCreate): Promise<Expense> {
  return api.post<Expense>('/expenses', payload);
}

export function deleteExpense(expenseId: number): Promise<void> {
  return api.delete(`/expenses/${expenseId}`);
}
