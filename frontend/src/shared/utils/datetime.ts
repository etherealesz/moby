import dayjs from 'dayjs';

/* ---------- Date Formatter ---------- */

/**
 * Format created at date to 'DD MMM YYYY' format
 *
 * @param date - The date string to format
 *
 * @returns Formatted date string
 *
 * @example
 * formatCreatedAt('2024-06-15T14:30:00Z'); // returns '15 Jun 2024'
 */
export function formatDisplayShortDate(date: Date): string {
  const formattedDate = dayjs(date).format('DD MMM YYYY');
  return formattedDate;
}

/**
 * Format date to 'DD MMMM YYYY' format
 *
 * @param date - The date string to format
 *
 * @returns Formatted date string
 */
export function formatDisplayLongDate(date: Date | string): string {
  const formattedDate = dayjs(date).format('DD MMMM YYYY');
  return formattedDate;
}

/**
 * Format date to 'DD-MM-YYYY' format
 *
 * @param date - The date string to format
 *
 * @returns Formatted date string
 *
 * @example
 * formatNumericDate('2024-06-15T14:30:00Z'); // returns '15-06-2024'
 */
export function formatNumericDate(date: Date | string): string {
  const formattedDate = dayjs(date).format('DD-MM-YYYY');
  return formattedDate;
}

/**
 * Format date to 'YYYY-MM-DD' format
 *
 * @param date - The date string to format
 *
 * @returns Formatted date string
 *
 * @example
 * formatISODate('15-06-2024'); // returns '2024-06-15'
 */
export function formatISODate(date: Date | string): string {
  const formattedDate = dayjs(date).format('YYYY-MM-DD');
  return formattedDate;
}

/* ---------- Time Formatter ---------- */

/**
 * Format time to 'HH:mm' format
 *
 * @param time - The time string to format
 *
 * @returns Formatted time string
 *
 * @example
 * formatTime('2024-06-15T14:30:00Z'); // returns '14:30'
 */
export function formatDisplayShortTime(time: Date | string): string {
  const formattedTime = dayjs(time).format('HH:mm');
  return formattedTime;
}

/**
 * Format time to 'HH:mm:ss' format
 *
 * @param time - The time string to format
 *
 * @returns Formatted time string
 *
 * @example
 * formatTime('2024-06-15T14:30:01Z'); // returns '14:30:01'
 */
export function formatDisplayLongTime(time: Date | string): string {
  const formatedTime = dayjs(time).format('HH:mm:ss');
  return formatedTime;
}

/* ---------- DateTime Formatter ---------- */

/**
 * Format date and time to 'DD MMM YYYY / HH:mm' format with a custom separator
 *
 * @param dateTime - The date and time string to format
 * @param separator - The separator string to use between date and
 *                    time (default is '/')
 *
 * @returns Formatted date and time string
 *
 * @example
 * formatDisplayDateTimeWithSeparator('2024-06-15T14:30:00Z', { separator: ' - ' }); // returns '15 Jun 2024 - 14:30'
 */
export function formatDisplayDateTimeWithSeparator(
  dateTime: Date | string,
  { separator = '/' }: { separator: string }
): string {
  const formattedDateTime = dayjs(dateTime).format(
    `DD MMM YYYY${separator}HH:mm`
  );
  return formattedDateTime;
}

export function formatISODateTimeWithoutSymbol(
  dateTime: Date | string
): string {
  const formattedDateTime = dayjs(dateTime).format('YYYYMMDDTHHmmss');
  return formattedDateTime;
}
