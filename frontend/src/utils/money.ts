const gbp = new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' });

export function formatPence(pence: number): string {
  return gbp.format(pence / 100);
}

/** Value for an editable cell: "1983.00", or "" for zero so empty cells stay clean. */
export function penceToInput(pence: number): string {
  return pence === 0 ? '' : (pence / 100).toFixed(2);
}

/**
 * Parse user input in pounds ("186", "£1,983.00", "9.75") to integer pence.
 * Returns null for input that isn't a valid amount. Empty input means zero.
 */
export function parsePoundsToPence(text: string): number | null {
  const cleaned = text.replace(/[£,\s]/g, '');
  if (cleaned === '') {
    return 0;
  }
  if (!/^\d+(\.\d{0,2})?$/.test(cleaned)) {
    return null;
  }
  return Math.round(parseFloat(cleaned) * 100);
}
