import { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import { copyForward, getYearView, setBudgetCell } from '../api/budgets';
import { createCategory, deleteCategory } from '../api/categories';
import type { CategoryGroup, YearView } from '../api/types';
import { ErrorNote } from '../components/ErrorNote';
import { SectionCard } from '../components/SectionCard';
import type { MonthRef, SectionRow } from '../components/SectionCard';
import { useAsync } from '../hooks/useAsync';
import { MONTHS_SHORT } from '../utils/dates';
import { formatPence } from '../utils/money';

// Editable sections rendered above the Spending group. SPENDING itself is
// rendered inside the group alongside Overspending / Other Spending.
const SECTIONS_ABOVE_SPENDING: CategoryGroup[] = ['income', 'bills'];

function clampMonth(value: number): number {
  return Math.min(12, Math.max(1, value));
}

function addMonths(ref: MonthRef, delta: number): MonthRef {
  const date = new Date(ref.year, ref.month - 1 + delta, 1);
  return { year: date.getFullYear(), month: date.getMonth() + 1 };
}

function monthLabel(ref: MonthRef): string {
  return `${MONTHS_SHORT[ref.month - 1]} ${String(ref.year).slice(-2)}`;
}

export function BudgetPage() {
  const params = useParams();
  const navigate = useNavigate();
  const now = new Date();
  const first: MonthRef = {
    year: Number(params.year) || now.getFullYear(),
    month: clampMonth(Number(params.month) || now.getMonth() + 1),
  };
  const months = [first, addMonths(first, 1)];

  // The API serves whole years; a Dec/Jan window needs two of them.
  const years = [...new Set(months.map((ref) => ref.year))];
  const { data, loading, error, reload } = useAsync(async () => {
    const views = await Promise.all(years.map((y) => getYearView(y)));
    return new Map<number, YearView>(views.map((view) => [view.year, view]));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [first.year, first.month]);

  function shiftMonth(delta: number) {
    const next = addMonths(first, delta);
    navigate(`/budget/${next.year}/${next.month}`);
  }

  async function handleSave(month: MonthRef, categoryId: number, amountPence: number) {
    try {
      await setBudgetCell(month.year, month.month, categoryId, amountPence);
    } finally {
      reload(); // re-sync totals (or revert the cell if the save failed)
    }
  }

  const [copying, setCopying] = useState(false);
  const [copyError, setCopyError] = useState<string | null>(null);

  async function handleCopyForward() {
    const confirmed = window.confirm(
      `Copy ${monthLabel(first)} amounts to every later month of ${first.year}? ` +
        'Existing values in those months will be overwritten.',
    );
    if (!confirmed) return;
    setCopying(true);
    setCopyError(null);
    try {
      await copyForward(first.year, first.month);
      reload();
    } catch (err) {
      setCopyError(err instanceof Error ? err.message : 'Copy failed');
    } finally {
      setCopying(false);
    }
  }

  async function handleAddCategory(group: CategoryGroup, name: string, sortOrder: number) {
    await createCategory({ name, group, sort_order: sortOrder });
    reload();
  }

  async function handleDeleteCategory(categoryId: number) {
    await deleteCategory(categoryId);
    reload();
  }

  function sectionFor(group: CategoryGroup) {
    const rows: SectionRow[] =
      data!
        .get(months[0].year)!
        .sections.find((s) => s.group === group)
        ?.rows.map((row) => ({ categoryId: row.category_id, name: row.name, amountsPence: [] })) ??
      [];
    const totals: number[] = [];
    for (const month of months) {
      const section = data!.get(month.year)!.sections.find((s) => s.group === group);
      totals.push(section?.totals_pence[month.month - 1] ?? 0);
      for (const row of rows) {
        const match = section?.rows.find((r) => r.category_id === row.categoryId);
        row.amountsPence.push(match?.amounts_pence[month.month - 1] ?? 0);
      }
    }
    return { rows, totals };
  }

  function savingsFor(month: MonthRef) {
    const view = data!.get(month.year)!;
    return {
      monthly: view.monthly_savings_pence[month.month - 1],
      cumulative: view.cumulative_savings_pence[month.month - 1],
    };
  }

  return (
    <div className="page">
      <header className="page-header centered">
        <h1>Budget</h1>
      </header>

      {error && <ErrorNote message={error} onRetry={reload} />}
      {!data && loading && <p className="muted">Loading…</p>}

      {data && (
        <>
          <div className="month-columns">
            <span />
            <span className="month-col">
              <button type="button" aria-label="Previous month" onClick={() => shiftMonth(-1)}>
                ‹
              </button>
              <Link to={`/months/${months[0].year}/${months[0].month}`}>
                {monthLabel(months[0])}
              </Link>
            </span>
            <span className="month-col">
              <Link to={`/months/${months[1].year}/${months[1].month}`}>
                {monthLabel(months[1])}
              </Link>
              <button type="button" aria-label="Next month" onClick={() => shiftMonth(1)}>
                ›
              </button>
            </span>
          </div>

          {SECTIONS_ABOVE_SPENDING.map((group) => {
            const { rows, totals } = sectionFor(group);
            return (
              <SectionCard
                key={group}
                group={group}
                rows={rows}
                months={months}
                totalsPence={totals}
                onSave={handleSave}
                onAdd={(name) => handleAddCategory(group, name, rows.length)}
                onDelete={(row) => handleDeleteCategory(row.categoryId)}
              />
            );
          })}

          {/* Spending / Overspending / Other Spending all describe outflows
              from the same planned-spending bucket, so visually we group
              them tight (small inner gap) with normal gaps before/after. */}
          <div className="spending-group">
            {(() => {
              const { rows, totals } = sectionFor('spending');
              return (
                <SectionCard
                  group="spending"
                  rows={rows}
                  months={months}
                  totalsPence={totals}
                  onSave={handleSave}
                  onAdd={(name) => handleAddCategory('spending', name, rows.length)}
                  onDelete={(row) => handleDeleteCategory(row.categoryId)}
                />
              );
            })()}

            <Link
              to={`/months/${first.year}/${first.month}`}
              className="other-summary"
              aria-label="Open Tracker to see what was overspent"
            >
              <span className="section-title">Overspending</span>
              {months.map((month) => {
                const view = data.get(month.year)!;
                // ?? 0 so a stale backend (without monthly_overspending_pence
                // in its response) can't crash the page mid-deploy.
                const pence = view.monthly_overspending_pence?.[month.month - 1] ?? 0;
                return (
                  <span
                    key={`${month.year}-${month.month}`}
                    className={pence > 0 ? 'value over' : 'value'}
                  >
                    {formatPence(pence)}
                  </span>
                );
              })}
            </Link>

            <Link
              to={`/other/${first.year}/${first.month}`}
              className="other-summary"
              aria-label="Open Other Spending"
            >
              <span className="section-title">Other Spending</span>
              {months.map((month) => {
                const view = data.get(month.year)!;
                const pence = view.monthly_unusual_pence?.[month.month - 1] ?? 0;
                return (
                  <span key={`${month.year}-${month.month}`} className="value">
                    {formatPence(pence)}
                  </span>
                );
              })}
            </Link>
          </div>

          {copyError && <ErrorNote message={copyError} />}
          {first.month < 12 && (
            <button
              type="button"
              className="copy-forward"
              disabled={copying}
              onClick={handleCopyForward}
            >
              {copying ? 'Copying…' : `Copy ${monthLabel(first)} to rest of ${first.year}`}
            </button>
          )}

          <section className="section-card savings-card">
            {(['monthly', 'cumulative'] as const).map((kind) => (
              <div key={kind} className="budget-row">
                <span className="name">
                  {kind === 'monthly' ? 'Monthly Savings' : 'Total Savings'}
                </span>
                {months.map((month) => {
                  const pence = savingsFor(month)[kind];
                  return (
                    <span
                      key={`${month.year}-${month.month}`}
                      className={pence < 0 ? 'value negative' : 'value'}
                    >
                      {formatPence(pence)}
                    </span>
                  );
                })}
              </div>
            ))}
          </section>
        </>
      )}
    </div>
  );
}
