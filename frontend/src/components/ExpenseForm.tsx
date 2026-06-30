import { useState } from 'react';
import type { FormEvent } from 'react';

import { createExpense } from '../api/expenses';
import type { ExpenseKind } from '../api/types';
import { parsePoundsToPence } from '../utils/money';
import { DatePicker } from './DatePicker';

interface Props {
  defaultDate: string; // ISO date inside the viewed month
  kind?: ExpenseKind;
  onCreated: () => void;
}

export function ExpenseForm({ defaultDate, kind = 'regular', onCreated }: Props) {
  const [date, setDate] = useState(defaultDate);
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
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
      });
      setAmount('');
      setDescription('');
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
