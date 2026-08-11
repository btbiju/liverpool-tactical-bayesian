const SURNAME_PARTICLES = new Set(['van', 'de', 'der', 'von', 'mac', 'mc', 'le', 'la', 'da', 'dos']);

// Short display surname for compact UI (pitch markers) -- handles compound
// surnames like "Mac Allister" or "van Dijk" that a naive last-word split breaks.
export function shortSurname(fullName) {
  const parts = fullName.trim().split(/\s+/);
  if (parts.length < 2) return fullName;
  const secondLast = parts[parts.length - 2].toLowerCase();
  if (SURNAME_PARTICLES.has(secondLast)) return parts.slice(-2).join(' ');
  return parts[parts.length - 1];
}
