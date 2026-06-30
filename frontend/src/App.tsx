import { Link, Navigate, Route, Routes, useLocation } from 'react-router-dom';

import { useAuth } from './auth/AuthContext';
import { LoadingScreen } from './components/LoadingScreen';
import { BudgetPage } from './pages/BudgetPage';
import { LoginPage } from './pages/LoginPage';
import { MonthPage } from './pages/MonthPage';
import { OtherSpendingPage } from './pages/OtherSpendingPage';

function currentMonthPath(): string {
  const now = new Date();
  return `/months/${now.getFullYear()}/${now.getMonth() + 1}`;
}

function currentBudgetPath(): string {
  const now = new Date();
  return `/budget/${now.getFullYear()}/${now.getMonth() + 1}`;
}

function currentOtherPath(): string {
  const now = new Date();
  return `/other/${now.getFullYear()}/${now.getMonth() + 1}`;
}

export default function App() {
  const { pathname } = useLocation();
  const { user, initializing, logout } = useAuth();

  if (initializing) {
    return <LoadingScreen />;
  }
  if (!user) {
    return <LoginPage />;
  }

  return (
    <div className="app">
      <main className="app-main">
        <Routes>
          <Route path="/" element={<Navigate to={currentMonthPath()} replace />} />
          <Route path="/budget/:year/:month" element={<BudgetPage />} />
          <Route path="/months/:year/:month" element={<MonthPage />} />
          <Route path="/other/:year/:month" element={<OtherSpendingPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <nav className="tab-bar">
        <Link
          to={currentBudgetPath()}
          className={pathname.startsWith('/budget') ? 'tab active' : 'tab'}
        >
          Budget
        </Link>
        <Link
          to={currentMonthPath()}
          className={pathname.startsWith('/months') ? 'tab active' : 'tab'}
        >
          Tracker
        </Link>
        <Link
          to={currentOtherPath()}
          className={pathname.startsWith('/other') ? 'tab active' : 'tab'}
        >
          Other
        </Link>
        <button type="button" className="tab tab-signout" onClick={logout}>
          Sign out
        </button>
      </nav>
    </div>
  );
}
