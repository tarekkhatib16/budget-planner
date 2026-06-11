import { useEffect, useState } from 'react';

/**
 * Becomes true after `delayMs` if `active` is still true; resets to false
 * when `active` goes false.
 *
 * Used to surface a "this is taking a while" message only once the user
 * has actually been waiting long enough to wonder. A warm request finishes
 * before the timer fires, so the message never appears.
 */
export function useSlowOperation(active: boolean, delayMs = 4000): boolean {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    if (!active) {
      setSlow(false);
      return;
    }
    const id = setTimeout(() => setSlow(true), delayMs);
    return () => clearTimeout(id);
  }, [active, delayMs]);
  return slow;
}
