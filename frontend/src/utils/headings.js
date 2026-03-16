/**
 * Convert a heading text string to a URL-safe anchor ID.
 * Must be used consistently in both the sidebar and the rendered headings.
 */
export function slugify(text) {
  return String(text)
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // strip emojis, special chars
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+$/, '');
}

/**
 * Extract h1–h3 headings from a markdown string, ignoring lines inside fenced code blocks.
 * Returns [{ id, text, level }]
 */
export function extractHeadings(markdown) {
  const results = [];
  let inFence = false;

  for (const line of markdown.split('\n')) {
    if (line.trimStart().startsWith('```')) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;

    const match = line.match(/^(#{1,3}) (.+)$/);
    if (match) {
      const level = match[1].length;
      const text = match[2].trim();
      results.push({ id: slugify(text), text, level });
    }
  }

  return results;
}
