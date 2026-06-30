import { useState } from 'react';
import type { FormEvent } from 'react';

import { createExpense } from '../api/expenses';
import type { Category, ExpenseKind } from '../api/types';
import { parsePoundsToPence } from '../utils/money';
import { DatePicker } from './DatePicker';

interface Props {
  defaultDate: string; // ISO date inside the viewed month
  kind?: ExpenseKind;
  /** Categories the user can pick from. Omit to hide the dropdown
   *  (used by the Other Spending tab). */
  categories?: Category[];
  onCreated: () => void;
}

export function ExpenseForm({ defaultDate, kind = 'regular', categories, onCreated }: Props) {
  const [date, setDate] = useState(defaultDate);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<string>(''); // '' = uncategorised
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const pence = parsePoundsToPence(amount);
    if (!pence || pence <= 0) {
      setError('Enter an amount greater than zero');
      return;
    }
    setSaving(true);
    setError(null);
    try {
      await createExpense({
        spend_date: date,
        amount_pence: pence,
        description: description.trim() || null,
        kind,
        category_id: categoryId ? Number(categoryId) : null,
      });
      setAmount('');
      setDescription('');
      // Keep the category sticky between adds — most users log several in a
      // row from the same category (e.g. a few Groceries entries).
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save expense');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="expense-form" onSubmit={handleSubmit}>
      <div className="expense-form-fields">
        <DatePicker value={date} onChange={setDate} />
        <input
          type="text"
          inputMode="decimal"
          aria-label="Amount in pounds"
          placeholder="£0.00"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          required
        />
        {categories && (
          <select
            aria-label="Category"
            value={categoryId}
            onChange={(event) => setCategoryId(event.target.value)}
          >
            <option value="">Uncategorised</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        )}
        <input
          type="text"
          aria-label="Description"
          placeholder="What was it? (optional)"
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <button type="submit" disabled={saving}>
          {saving ? 'Adding…' : 'Add'}
        </button>
      </div>
      {error && <p className="form-error">{error}</p>}
    </form>
  );
}
