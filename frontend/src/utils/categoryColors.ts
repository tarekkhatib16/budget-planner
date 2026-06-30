// Stable colour palette for Spending categories. Indexing by sort_order
// (not category id) keeps colours visually consistent when categories are
// added or removed.
const PALETTE = [
  '#1c4587', // navy
  '#d23f31', // red
  '#1e8e3e', // green
  '#f9ab00', // amber
  '#9334e6', // purple
  '#129eaf', // teal
  '#e8710a', // orange
  '#b85d8a', // rose
];

export const UNCATEGORISED_COLOR = '#7d8aa3'; // muted slate, distinct from palette

export function colorForIndex(index: number): string {
  return PALETTE[index % PALETTE.length];
}
