import type { WeekSummary } from '../api/types';
import { formatDayShort, formatRange } from '../utils/dates';
import { formatPence } from '../utils/money';

interface Props {
  week: WeekSummary;
  isCurrent: boolean;
  onDeleteExpense: (expenseId: number) => void;
}

export function WeekCard({ week, isCurrent, onDeleteExpense }: Props) {
  return (
    <section className={isCurrent ? 'week-card current' : 'week-card'}>
      <header className="week-card-header">
        <h2>
          Week {week.index}
          <span className="week-range"> · {formatRange(week.start, week.end)}</span>
        </h2>
        <span className="week-allowance">{formatPence(week.allowance_pence)}</span>
      </header>
      <div className="week-stats">
        <span>
          Spent <strong>{formatPence(week.spent_pence)}</strong>
        </span>
        <span className={week.saved_pence < 0 ? 'negative' : 'positive'}>
          {week.saved_pence < 0 ? 'Over by ' : 'Saved '}
          <strong>{formatPence(Math.abs(week.saved_pence))}</strong>
        </span>
      </div>
      {week.expenses.length > 0 && (
        <ul className="expense-list">
          {week.expenses.map((expense) => (
            <li key={expense.id}>
              <span className="expense-date">{formatDayShort(expense.spend_date)}</span>
              <span className="expense-description">{expense.description ?? '—'}</span>
              <span className="expense-amount">{formatPence(expense.amount_pence)}</span>
              <button
                type="button"
                className="expense-delete"
                aria-label="Delete expense"
                onClick={() => onDeleteExpense(expense.id)}
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
