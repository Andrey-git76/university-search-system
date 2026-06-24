export function highlightQuery(text: string, query: string): string {
  const words = query
    .trim()
    .split(/\s+/)
    .filter(Boolean)
    .map((word) => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

  if (words.length === 0) {
    return escapeHtml(text);
  }

  const pattern = new RegExp(`(${words.join('|')})`, 'gi');
  return escapeHtml(text).replace(
    pattern,
    '<mark class="highlight-match">$1</mark>'
  );
}

function escapeHtml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function sanitizeHighlight(html: string): string {
  return html.replace(/<mark>/g, '<mark class="highlight-match">');
}
