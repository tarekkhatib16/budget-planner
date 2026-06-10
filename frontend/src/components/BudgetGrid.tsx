import { Link } from 'react-router-dom';

import type { CategoryGroup, YearView } from '../api/types';
import { MONTHS_SHORT } from '../utils/dates';
import { formatPence } from '../utils/money';
import { BudgetCellInput } from './BudgetCellInput';

const GROUP_LABELS: Record<CategoryGroup, string> = {
  income: 'Income',
  bills: 'Bills',
  spending: 'Spending',
  holiday: 'Holiday',
  debt: 'Debt',
};

const GROUP_TOTAL_LABELS: Record<CategoryGroup, string | null> = {
  income: 'Total Incoming',
  bills: 'Total Bills',
  spending: 'Total Spending',
  holiday: 'Holiday Spending',
  debt: null, // debt rows are balances; summing them means nothing
};

interface Props {
  view: YearView;
  onCellSave: (month: number, categoryId: number, amountPence: number) => void;
}

function MoneyRow({ label, values, signed }: { label: string; values: number[]; signed?: boolean }) {
  return (
    <tr className="computed-row">
      <th className="row-label">{label}</th>
      {values.map((pence, i) => (
        <td key={i} className={signed && pence < 0 ? 'negative' : undefined}>
          {formatPence(pence)}
        </td>
      ))}
    </tr>
  );
}

export function BudgetGrid({ view, onCellSave }: Props) {
  return (
    <div className="grid-scroll">
      <table className="budget-grid">
        <thead>
          <tr>
            <th className="row-label corner" aria-label="Category" />
            {MONTHS_SHORT.map((name, i) => (
              <th key={name}>
                <Link to={`/months/${view.year}/${i + 1}`}>{name}</Link>
              </th>
            ))}
          </tr>
        </thead>
        {view.sections.map((section) => (
          <tbody key={section.group}>
            <tr className="section-row">
              <th className="row-label" colSpan={13}>
                {GROUP_LABELS[section.group]}
              </th>
            </tr>
            {section.rows.map((row) => (
              <tr key={row.category_id}>
                <th className="row-label">{row.name}</th>
                {row.amounts_pence.map((pence, i) => (
                  <td key={i}>
                    <BudgetCellInput
                      valuePence={pence}
                      onSave={(newPence) => onCellSave(i + 1, row.category_id, newPence)}
                    />
                  </td>
                ))}
              </tr>
            ))}
            {GROUP_TOTAL_LABELS[section.group] && (
              <MoneyRow label={GROUP_TOTAL_LABELS[section.group]!} values={section.totals_pence} />
            )}
          </tbody>
        ))}
        <tbody>
          <tr className="section-row">
            <th className="row-label" colSpan={13}>
              Savings
            </th>
          </tr>
          <MoneyRow label="Monthly Savings" values={view.monthly_savings_pence} signed />
          <MoneyRow label="Total Savings" values={view.cumulative_savings_pence} signed />
        </tbody>
      </table>
    </div>
  );
}
