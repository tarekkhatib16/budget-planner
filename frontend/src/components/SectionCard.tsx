import { useState } from 'react';
import type { FormEvent } from 'react';

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
  onAdd: (name: string) => Promise<void>;
  onDelete: (row: SectionRow) => Promise<void>;
}

/**
 * One collapsible budget section. Collapsed it shows just the group totals
 * for the visible months; expanded it reveals each category with editable
 * amounts, plus controls to add and remove categories.
 */
export function SectionCard({ group, rows, months, totalsPence, onSave, onAdd, onDelete }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [newName, setNewName] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleAdd(event: FormEvent) {
    event.preventDefault();
    const name = newName.trim();
    if (!name) return;
    setBusy(true);
    setError(null);
    try {
      await onAdd(name);
      setNewName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add category');
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete(row: SectionRow) {
    if (!window.confirm(`Delete "${row.name}" and its budgeted amounts?`)) return;
    setError(null);
    try {
      await onDelete(row);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete category');
    }
  }

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
      {expanded && (
        <>
          {rows.map((row) => (
            <div key={row.categoryId} className="budget-row">
              <span className="name">
                <button
                  type="button"
                  className="row-delete"
                  aria-label={`Delete ${row.name}`}
                  onClick={() => handleDelete(row)}
                >
                  ×
                </button>
                {row.name}
              </span>
              {months.map((month, i) => (
                <BudgetCellInput
                  key={`${month.year}-${month.month}`}
                  valuePence={row.amountsPence[i]}
                  onSave={(pence) => onSave(month, row.categoryId, pence)}
                />
              ))}
            </div>
          ))}
          <form className="add-row" onSubmit={handleAdd}>
            <input
              type="text"
              aria-label={`New ${GROUP_LABELS[group]} category name`}
              placeholder="Add category…"
              maxLength={100}
              value={newName}
              onChange={(event) => {
                setNewName(event.target.value);
                setError(null);
              }}
            />
            <button type="submit" disabled={busy || !newName.trim()}>
              Add
            </button>
          </form>
          {error && <p className="form-error section-error">{error}</p>}
        </>
      )}
    </section>
  );
}
