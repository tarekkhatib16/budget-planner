import { useState } from 'react';
import type { FormEvent } from 'react';

import { useAuth } from '../auth/AuthContext';
import { useSlowOperation } from '../hooks/useSlowOperation';

export function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const slow = useSlowOperation(busy);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === 'login') {
        await login(email, password);
      } else {
        await register(email, password);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <h1>Budget Planner</h1>
        <p className="muted">
          {mode === 'login' ? 'Sign in to your budget' : 'Create your account'}
        </p>
        <input
          type="email"
          autoComplete="email"
          placeholder="Email"
          aria-label="Email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          required
        />
        <input
          type="password"
          autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
          placeholder={mode === 'login' ? 'Password' : 'Password (min 8 characters)'}
          aria-label="Password"
          minLength={mode === 'register' ? 8 : undefined}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          required
        />
        {error && <p className="form-error">{error}</p>}
        <button type="submit" disabled={busy}>
          {busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}
        </button>
        {slow && (
          <p className="muted login-slow">
            Waking up the server — this can take up to a minute.
          </p>
        )}
        <button
          type="button"
          className="link-button"
          onClick={() => {
            setMode(mode === 'login' ? 'register' : 'login');
            setError(null);
          }}
        >
          {mode === 'login' ? 'Need an account? Register' : 'Have an account? Sign in'}
        </button>
      </form>
    </div>
  );
}
