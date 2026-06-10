import { useNavigate, useParams } from 'react-router-dom';

import { deleteExpense } from '../api/expenses';
import { getMonthSummary } from '../api/months';
import { ErrorNote } from '../components/ErrorNote';
import { ExpenseForm } from '../components/ExpenseForm';
import { WeekCard } from '../components/WeekCard';
import { useAsync } from '../hooks/useAsync';
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

          <ExpenseForm key={`${year}-${month}`} defaultDate={defaultDate} onCreated={reload} />

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
