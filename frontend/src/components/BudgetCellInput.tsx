import { useState } from 'react';

import { parsePoundsToPence, penceToInput } from '../utils/money';

interface Props {
  valuePence: number;
  onSave: (pence: number) => void;
}

/**
 * One editable cell of the budget grid. Shows pounds, keeps a local draft
 * while focused, and commits on blur/Enter only if the value changed.
 */
export function BudgetCellInput({ valuePence, onSave }: Props) {
  const [draft, setDraft] = useState<string | null>(null);
  const [invalid, setInvalid] = useState(false);

  function commit() {
    if (draft === null) return;
    const pence = parsePoundsToPence(draft);
    if (pence === null) {
      setInvalid(true);
      setDraft(null); // revert to the saved value
      return;
    }
    setDraft(null);
    setInvalid(false);
    if (pence !== valuePence) {
      onSave(pence);
    }
  }

  return (
    <input
      className={invalid ? 'cell-input invalid' : 'cell-input'}
      type="text"
      inputMode="decimal"
      value={draft ?? penceToInput(valuePence)}
      onChange={(event) => {
        setDraft(event.target.value);
        setInvalid(false);
      }}
      onFocus={(event) => event.target.select()}
      onBlur={commit}
      onKeyDown={(event) => {
        if (event.key === 'Enter') event.currentTarget.blur();
      }}
    />
  );
}
