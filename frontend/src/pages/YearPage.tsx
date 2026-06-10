import { useNavigate, useParams } from 'react-router-dom';

import { getYearView, setBudgetCell } from '../api/budgets';
import { BudgetGrid } from '../components/BudgetGrid';
import { ErrorNote } from '../components/ErrorNote';
import { useAsync } from '../hooks/useAsync';

export function YearPage() {
  const params = useParams();
  const year = Number(params.year) || new Date().getFullYear();
  const navigate = useNavigate();
  const { data, loading, error, reload } = useAsync(() => getYearView(year), [year]);

  async function handleCellSave(month: number, categoryId: number, amountPence: number) {
    try {
      await setBudgetCell(year, month, categoryId, amountPence);
    } finally {
      reload(); // re-sync totals (or revert the cell if the save failed)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <button type="button" aria-label="Previous year" onClick={() => navigate(`/year/${year - 1}`)}>
          ‹
        </button>
        <h1>{year} Budget</h1>
        <button type="button" aria-label="Next year" onClick={() => navigate(`/year/${year + 1}`)}>
          ›
        </button>
      </header>
      {error && <ErrorNote message={error} onRetry={reload} />}
      {data ? (
        <BudgetGrid view={data} onCellSave={handleCellSave} />
      ) : (
        loading && <p className="muted">Loading…</p>
      )}
    </div>
  );
}
