import { useNavigate, useParams } from 'react-router-dom';

import { api } from '../api/client';
import { deleteExpense } from '../api/expenses';
import { getMonthSummary } from '../api/months';
import type { Category } from '../api/types';
import { ErrorNote } from '../components/ErrorNote';
import { ExpenseForm } from '../components/ExpenseForm';
import { PieChart } from '../components/PieChart';
import type { PieSlice } from '../components/PieChart';
import { WeekCard } from '../components/WeekCard';
import { useAsync } from '../hooks/useAsync';
import { UNCATEGORISED_COLOR, colorForIndex } from '../utils/categoryColors';
import { MONTHS_LONG, parseISODate, toISODate } from '../utils/dates';
import { formatPence } from '../utils/money';

function clampMonth(value: number): number {
  return Math.min(12, Math.max(1, value));
}

export function MonthPage() {
  const params = useParams();
  const navigate = useNavigate();
  const now = new Date();
  const year = Number(params.year) || now.getFullYear();
  const month = clampMonth(Number(params.month) || now.getMonth() + 1);

  // Categories rarely change while the user is on this page; fetch once.
  // The month summary reloads on add/delete, but categories don't need to.
  const categoriesAsync = useAsync(() => api.get<Category[]>('/categories'), []);
  const spendingCategories = (categoriesAsync.data ?? []).filter(
    (category) => category.group === 'spending',
  );

  const { data, loading, error, reload } = useAsync(
    () => getMonthSummary(year, month),
    [year, month],
  );

  function shiftMonth(delta: number) {
    const shifted = new Date(year, month - 1 + delta, 1);
    navigate(`/months/${shifted.getFullYear()}/${shifted.getMonth() + 1}`);
  }

  async function handleDeleteExpense(expenseId: number) {
    await deleteExpense(expenseId);
    reload();
  }

  const today = new Date();
  const isCurrentMonth = today.getFullYear() === year && today.getMonth() + 1 === month;
  const defaultDate = isCurrentMonth ? toISODate(today) : `${year}-${String(month).padStart(2, '0')}-01`;

  // Build pie slices from the breakdown: drop £0 categories (user's
  // explicit ask), assign stable colours by sort_order so the same
  // category looks the same wherever it shows up.
  const slices: PieSlice[] = (data?.category_breakdown ?? [])
    .filter((item) => item.amount_pence > 0)
    .map((item) => {
      if (item.category_id === null) {
        return {
          key: 'uncategorised',
          label: item.name,
          amountPence: item.amount_pence,
          color: UNCATEGORISED_COLOR,
        };
      }
      const sortOrder =
        spendingCategories.find((c) => c.id === item.category_id)?.sort_order ?? 0;
      return {
        key: String(item.category_id),
        label: item.name,
        amountPence: item.amount_pence,
        color: colorForIndex(sortOrder),
      };
    });

  return (
    <div className="page">
      <header className="page-header">
        <button type="button" aria-label="Previous month" onClick={() => shiftMonth(-1)}>
          ‹
        </button>
        <h1>
          {MONTHS_LONG[month - 1]} {year}
        </h1>
        <button type="button" aria-label="Next month" onClick={() => shiftMonth(1)}>
          ›
        </button>
      </header>

      {error && <ErrorNote message={error} onRetry={reload} />}
      {!data && loading && <p className="muted">Loading…</p>}

      {data && (
        <>
          <div className="summary-bar">
            <div className="stat">
              <span className="stat-label">Budget</span>
              <span className="stat-value">{formatPence(data.spending_budget_pence)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Spent</span>
              <span className="stat-value">{formatPence(data.total_spent_pence)}</span>
            </div>
            <div className="stat">
              <span className="stat-label">{data.total_saved_pence < 0 ? 'Over' : 'Saved'}</span>
              <span
                className={`stat-value ${data.total_saved_pence < 0 ? 'negative' : 'positive'}`}
              >
                {formatPence(Math.abs(data.total_saved_pence))}
              </span>
            </div>
          </div>

          {data.spending_budget_pence === 0 && (
            <p className="muted">
              No spending budget set for this month yet — add amounts to the Spending section in
              the Budget tab.
            </p>
          )}

          <PieChart slices={slices} />

          <ExpenseForm
            key={`${year}-${month}`}
            defaultDate={defaultDate}
            categories={spendingCategories}
            onCreated={reload}
          />

          {data.weeks.map((week) => {
            const start = parseISODate(week.start);
            const end = parseISODate(week.end);
            end.setHours(23, 59, 59);
            const isCurrentWeek = today >= start && today <= end;
            return (
              <WeekCard
                key={week.index}
                week={week}
                isCurrent={isCurrentWeek}
                onDeleteExpense={handleDeleteExpense}
              />
            );
          })}
        </>
      )}
    </div>
  );
}
