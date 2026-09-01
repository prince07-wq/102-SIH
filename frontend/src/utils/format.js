// Indian numbering system formatters (lakh/crore grouping).

const inrGroupFormatter = new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 });

export function formatINR(amount) {
  if (amount === null || amount === undefined || Number.isNaN(amount)) return '\u2014';
  return `\u20B9${inrGroupFormatter.format(Math.round(amount))}`;
}

export function formatCompactINR(amount) {
  if (amount === null || amount === undefined) return '\u2014';
  const crore = 1e7;
  const lakh = 1e5;
  if (amount >= crore) return `\u20B9${(amount / crore).toFixed(amount >= 100 * crore ? 0 : 1)} Cr`;
  if (amount >= lakh) return `\u20B9${(amount / lakh).toFixed(1)} L`;
  return formatINR(amount);
}

export function formatNumberIN(value) {
  if (value === null || value === undefined) return '\u2014';
  return inrGroupFormatter.format(value);
}
