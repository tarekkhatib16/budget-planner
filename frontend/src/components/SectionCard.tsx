import { useState } from 'react';

import type { CategoryGroup } from '../api/types';
import { formatPence } from '../utils/money';
import { BudgetCellInput } from './BudgetCellInput';

export interface MonthRef {
  year: number;
  month: number;
}

export interface SectionRow {
  categoryId: number;
  name: string;
  /** Budgeted amount for each visible month, aligned with the months prop. */
  amountsPence: number[];
}

const GROUP_LABELS: Record<CategoryGroup, string> = {
  income: 'Income',
  bills: 'Bills',
  spending: 'Spending',
  holiday: 'Holiday',
  debt: 'Debt',
};

interface Props {
  group: CategoryGroup;
  rows: SectionRow[];
  months: MonthRef[];
  /** Section total for each visible month. */
  totalsPence: number[];
  onSave: (month: MonthRef, categoryId: number, amountPence: number) => void;
}

/**
 * One collapsible budget section. Collapsed it shows just the group totals
 * for the visible months; expanded it reveals each category with editable
 * amounts.
 */
export function SectionCard({ group, rows, months, totalsPence, onSave }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <section className="section-card">
      <button
        type="button"
        className="section-card-header"
        aria-expanded={expanded}
        onClick={() => setExpanded(!expanded)}
      >
        <span className="section-title">
          <span className={expanded ? 'chevron open' : 'chevron'}>›</span>
          {GROUP_LABELS[group]}
          <span className="section-count">{rows.length}</span>
        </span>
        {totalsPence.map((pence, i) => (
          <span key={i} className="value">
            {formatPence(pence)}
          </span>
        ))}
      </button>
      {expanded &&
        rows.map((row) => (
          <div key={row.categoryId} className="budget-row">
            <span className="name">{row.name}</span>
            {months.map((month, i) => (
              <BudgetCellInput
                key={`${month.year}-${month.month}`}
                valuePence={row.amountsPence[i]}
                onSave={(pence) => onSave(month, row.categoryId, pence)}
              />
            ))}
          </div>
        ))}
    </section>
  );
}
