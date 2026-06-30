// Mirrors the backend's Pydantic schemas (api/schemas/*). All money values
// are integer pence.

export interface User {
  id: number;
  email: string;
}

export type CategoryGroup = 'income' | 'bills' | 'spending' | 'holiday' | 'debt';

export interface Category {
  id: number;
  name: string;
  group: CategoryGroup;
  sort_order: number;
}

export interface CategoryRow {
  category_id: number;
  name: string;
  amounts_pence: number[]; // 12 values, index 0 = January
}

export interface GroupSection {
  group: CategoryGroup;
  rows: CategoryRow[];
  totals_pence: number[];
}

export interface YearView {
  year: number;
  sections: GroupSection[];
  monthly_overspending_pence: number[];
  monthly_unusual_pence: number[];
  monthly_savings_pence: number[];
  cumulative_savings_pence: number[];
}

export type ExpenseKind = 'regular' | 'unusual';

export interface Expense {
  id: number;
  spend_date: string; // ISO date
  amount_pence: number;
  description: string | null;
  kind: ExpenseKind;
  category_id: number | null;
}

export interface CategoryBreakdownItem {
  category_id: number | null;
  name: string;
  amount_pence: number;
}

export interface WeekSummary {
  index: number;
  start: string;
  end: string;
  allowance_pence: number;
  spent_pence: number;
  saved_pence: number;
  expenses: Expense[];
}

export interface MonthSummary {
  year: number;
  month: number;
  spending_budget_pence: number;
  total_spent_pence: number;
  total_saved_pence: number;
  weeks: WeekSummary[];
  category_breakdown: CategoryBreakdownItem[];
}
