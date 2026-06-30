import { useEffect, useRef, useState } from 'react';

import type { Category } from '../api/types';
import { UNCATEGORISED_COLOR, colorForIndex } from '../utils/categoryColors';

interface Props {
  categories: Category[];
  value: number | null;
  onChange: (value: number | null) => void;
}

/**
 * App-styled replacement for <select>, matching the DatePicker pattern.
 * iOS shows a wheel picker for native selects, which doesn't match the
 * rest of the app — this renders a popover with category names and
 * matching colour swatches from the pie palette.
 */
export function CategorySelect({ categories, value, onChange }: Props) {
  const [open, setOpen] = useState(false);
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

  const selected = value !== null ? categories.find((c) => c.id === value) : null;
  const selectedColor = selected ? colorForIndex(selected.sort_order) : UNCATEGORISED_COLOR;
  const selectedLabel = selected ? selected.name : 'Uncategorised';

  function pick(next: number | null) {
    onChange(next);
    setOpen(false);
  }

  return (
    <div className="category-select" ref={rootRef}>
      <button
        type="button"
        className="category-field"
        aria-label="Category"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen(!open)}
      >
        <span className="swatch" style={{ background: selectedColor }} aria-hidden="true" />
        <span className="label">{selectedLabel}</span>
        <span className="caret" aria-hidden="true">
          ▾
        </span>
      </button>
      {open && (
        <ul className="category-menu" role="listbox">
          <li>
            <button
              type="button"
              className={value === null ? 'item selected' : 'item'}
              role="option"
              aria-selected={value === null}
              onClick={() => pick(null)}
            >
              <span
                className="swatch"
                style={{ background: UNCATEGORISED_COLOR }}
                aria-hidden="true"
              />
              Uncategorised
            </button>
          </li>
          {categories.map((category) => (
            <li key={category.id}>
              <button
                type="button"
                className={value === category.id ? 'item selected' : 'item'}
                role="option"
                aria-selected={value === category.id}
                onClick={() => pick(category.id)}
              >
                <span
                  className="swatch"
                  style={{ background: colorForIndex(category.sort_order) }}
                  aria-hidden="true"
                />
                {category.name}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
