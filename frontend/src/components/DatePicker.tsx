import { useEffect, useRef, useState } from 'react';

import { MONTHS_LONG, MONTHS_SHORT, parseISODate, toISODate } from '../utils/dates';

interface Props {
  value: string; // ISO date
  onChange: (iso: string) => void;
}

const WEEKDAYS = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

/**
 * App-styled replacement for <input type="date">, whose popup calendar is
 * browser chrome and can't be themed. A button shows the selected date;
 * tapping it opens a popover calendar (Monday-first, like the tracker).
 */
export function DatePicker({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const selected = parseISODate(value);
  // The month shown in the popover; navigable independently of the selection.
  const [view, setView] = useState({ year: selected.getFullYear(), month: selected.getMonth() });
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: PointerEvent) {
      if (rootRef.current && !rootRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === 'Escape') setOpen(false);
    }
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  function toggle() {
    setView({ year: selected.getFullYear(), month: selected.getMonth() });
    setOpen(!open);
  }

  function shiftView(delta: number) {
    const shifted = new Date(view.year, view.month + delta, 1);
    setView({ year: shifted.getFullYear(), month: shifted.getMonth() });
  }

  function pick(iso: string) {
    onChange(iso);
    setOpen(false);
  }

  const daysInView = new Date(view.year, view.month + 1, 0).getDate();
  // getDay() is Sunday-first; rotate so Monday starts the week.
  const leadingBlanks = (new Date(view.year, view.month, 1).getDay() + 6) % 7;
  const todayISO = toISODate(new Date());

  return (
    <div className="date-picker" ref={rootRef}>
      <button
        type="button"
        className="date-field"
        aria-label="Date"
        aria-haspopup="dialog"
        aria-expanded={open}
        onClick={toggle}
      >
        {selected.getDate()} {MONTHS_SHORT[selected.getMonth()]} {selected.getFullYear()}
      </button>
      {open && (
        <div className="calendar-pop" role="dialog" aria-label="Choose date">
          <div className="calendar-header">
            <button type="button" aria-label="Previous month" onClick={() => shiftView(-1)}>
              ‹
            </button>
            <span>
              {MONTHS_LONG[view.month]} {view.year}
            </span>
            <button type="button" aria-label="Next month" onClick={() => shiftView(1)}>
              ›
            </button>
          </div>
          <div className="calendar-grid">
            {WEEKDAYS.map((day, i) => (
              <span key={i} className="weekday">
                {day}
              </span>
            ))}
            {Array.from({ length: leadingBlanks }, (_, i) => (
              <span key={`blank-${i}`} />
            ))}
            {Array.from({ length: daysInView }, (_, i) => {
              const iso = toISODate(new Date(view.year, view.month, i + 1));
              const classes = ['day'];
              if (iso === value) classes.push('selected');
              if (iso === todayISO) classes.push('today');
              return (
                <button
                  key={iso}
                  type="button"
                  className={classes.join(' ')}
                  onClick={() => pick(iso)}
                >
                  {i + 1}
                </button>
              );
            })}
          </div>
          <button type="button" className="calendar-today" onClick={() => pick(todayISO)}>
            Today
          </button>
        </div>
      )}
    </div>
  );
}
