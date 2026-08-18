/**
 * Format a number string to Indonesian Rupiah currency format
 *
 * @param value - The number string to format
 *
 * @returns Formatted currency string
 *
 * @example
 * formatCurrency('1000000'); // returns 'Rp1.000.000,00'
 */
export function formatDisplayCurrency(value: string) {
  const tempValue = parseFloat(value);
  return tempValue.toLocaleString('id-ID', {
    style: 'currency',
    currency: 'IDR',
  });
}
