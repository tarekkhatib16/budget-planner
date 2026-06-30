import { useNavigate, useParams } from 'react-router-dom';

import { deleteExpense, listExpenses } from '../api/expenses';
import { ErrorNote } from '../components/ErrorNote';
import { ExpenseForm } from '../components/ExpenseForm';
import { useAsync } from '../hooks/useAsync';
import { MONTHS_LONG, formatDayShort, toISODate } from '../utils/dates';
import { formatPence } from '../utils/money';

function clampMonth(value: number): number {
  return Math.min(12, Math.max(1, value));
}

/**
 * One-off expenses (holidays, big purchases) — logged like the tracker but
 * with no weekly bucketing and no budget to match against. The actuals
 * surface on the Budget tab as the "Other Spending" summary row.
 */
export function OtherSpendingPage() {
  const params = useParams();
  const navigate = useNavigate();
  const now = new Date();
  const year = Number(params.year) || now.getFullYear();
  const month = clampMonth(Number(params.month) || now.getMonth() + 1);

  const { data, loading, error, reload } = useAsync(
    () => listExpenses(year, month, 'unusual'),
    [year, month],
  );

  function shiftMonth(delta: number) {
    const shifted = new Date(year, month - 1 + delta, 1);
    navigate(`/other/${shifted.getFullYear()}/${shifted.getMonth() + 1}`);
  }

  async function handleDelete(expenseId: number) {
    await deleteExpense(expenseId);
    reload();
  }

  const isCurrentMonth = now.getFullYear() === year && now.getMonth() + 1 === month;
  const defaultDate = isCurrentMonth
    ? toISODate(now)
    : `${year}-${String(month).padStart(2, '0')}-01`;

  const total = (data ?? []).reduce((sum, e) => sum + e.amount_pence, 0);

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
              <span className="stat-label">Other spending</span>
              <span className="stat-value">{formatPence(total)}</span>
            </div>
          </div>

          <ExpenseForm
            key={`${year}-${month}`}
            defaultDate={defaultDate}
            kind="unusual"
            onCreated={reload}
          />

          {data.length === 0 ? (
            <p className="muted">No unusual expenses logged for this month yet.</p>
          ) : (
            <section className="section-card">
              <ul className="expense-list flat">
                {data.map((expense) => (
                  <li key={expense.id}>
                    <span className="expense-date">{formatDayShort(expense.spend_date)}</span>
                    <span className="expense-description">{expense.description ?? '—'}</span>
                    <span className="expense-amount">{formatPence(expense.amount_pence)}</span>
                    <button
                      type="button"
                      className="expense-delete"
                      aria-label="Delete expense"
                      onClick={() => handleDelete(expense.id)}
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </div>
  );
}
