import { formatPence } from '../utils/money';

export interface PieSlice {
  key: string;
  label: string;
  amountPence: number;
  color: string;
}

interface Props {
  slices: PieSlice[];
}

const SIZE = 120;
const RADIUS = SIZE / 2 - 2;
const CENTER = SIZE / 2;

/**
 * Small SVG pie chart with a legend. Zero-value slices are filtered out by
 * the caller (the user wants categories with £0 hidden).
 *
 * Single-slice case is special: an arc that covers 360° is degenerate (the
 * start and end point are identical), so we draw a full circle instead.
 */
export function PieChart({ slices }: Props) {
  const total = slices.reduce((s, c) => s + c.amountPence, 0);
  if (total === 0 || slices.length === 0) return null;

  return (
    <div className="pie-chart">
      <svg
        width={SIZE}
        height={SIZE}
        viewBox={`0 0 ${SIZE} ${SIZE}`}
        role="img"
        aria-label={`Spending breakdown: ${slices.map((s) => s.label).join(', ')}`}
      >
        {slices.length === 1 ? (
          <circle cx={CENTER} cy={CENTER} r={RADIUS} fill={slices[0].color} />
        ) : (
          slices.reduce<{ acc: number; out: React.ReactNode[] }>(
            ({ acc, out }, slice) => {
              const start = (acc / total) * 2 * Math.PI - Math.PI / 2;
              const nextAcc = acc + slice.amountPence;
              const end = (nextAcc / total) * 2 * Math.PI - Math.PI / 2;
              const x1 = CENTER + RADIUS * Math.cos(start);
              const y1 = CENTER + RADIUS * Math.sin(start);
              const x2 = CENTER + RADIUS * Math.cos(end);
              const y2 = CENTER + RADIUS * Math.sin(end);
              const largeArc = end - start > Math.PI ? 1 : 0;
              const path = `M ${CENTER} ${CENTER} L ${x1} ${y1} A ${RADIUS} ${RADIUS} 0 ${largeArc} 1 ${x2} ${y2} Z`;
              out.push(<path key={slice.key} d={path} fill={slice.color} />);
              return { acc: nextAcc, out };
            },
            { acc: 0, out: [] },
          ).out
        )}
      </svg>
      <ul className="pie-legend">
        {slices.map((slice) => (
          <li key={slice.key}>
            <span className="swatch" style={{ background: slice.color }} aria-hidden="true" />
            <span className="legend-name">{slice.label}</span>
            <span className="legend-amount">{formatPence(slice.amountPence)}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
