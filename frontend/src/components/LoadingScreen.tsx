import { useSlowOperation } from '../hooks/useSlowOperation';

/**
 * Full-page loading view shown while the app waits on the API.
 *
 * Render's free tier sleeps after ~15 minutes idle, so the first request
 * after a pause can take 30-60s while the dyno wakes. We don't want to
 * cry wolf on every load, so the explanation only appears after a few
 * seconds of actual waiting.
 */
export function LoadingScreen() {
  const slow = useSlowOperation(true);

  return (
    <div className="loading-screen">
      <div className="loading-mark">£</div>
      <div className="loading-spinner" aria-hidden="true" />
      <p className={slow ? 'loading-message' : 'loading-message subtle'}>
        {slow
          ? 'Waking up the server — this can take up to a minute.'
          : 'Loading…'}
      </p>
    </div>
  );
}
