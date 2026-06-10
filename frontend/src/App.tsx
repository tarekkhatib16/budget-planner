import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';

import { MonthPage } from './pages/MonthPage';
import { YearPage } from './pages/YearPage';

function currentMonthPath(): string {
  const now = new Date();
  return `/months/${now.getFullYear()}/${now.getMonth() + 1}`;
}

export default function App() {
  const { pathname } = useLocation();

  return (
    <div className="app">
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to={currentMonthPath()} replace />} />
          <Route path="/year/:year" element={<YearPage />} />
          <Route path="/months/:year/:month" element={<MonthPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <nav className="tab-bar">
        <Link
          to={`/year/${new Date().getFullYear()}`}
          className={pathname.startsWith('/year') ? 'tab active' : 'tab'}
        >
          Budget
        </Link>
        <Link
          to={currentMonthPath()}
          className={pathname.startsWith('/months') ? 'tab active' : 'tab'}
        >
          Tracker
        </Link>
      </nav>
    </div>
  );
}
