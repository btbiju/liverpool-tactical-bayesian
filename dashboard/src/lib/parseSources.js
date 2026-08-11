// Every profile's notes array ends with one note shaped like:
//   "Sources: name1, name2 (context), name3 -- via web search 2026-08-10."
// This splits that into a { entries: [{name, context}], via } structure for
// table rendering, and returns the remaining notes separately.
export function splitNotesAndSources(notes) {
  const rest = [];
  let sources = null;

  for (const note of notes ?? []) {
    if (sources == null && /^Sources:/i.test(note.trim())) {
      sources = parseSourcesLine(note.trim());
    } else {
      rest.push(note);
    }
  }

  return { notes: rest, sources };
}

function parseSourcesLine(line) {
  const body = line.replace(/^Sources:\s*/i, '').replace(/\.$/, '');
  const viaMatch = body.match(/\s*--\s*via\s+(.+)$/i);
  const via = viaMatch ? viaMatch[1].trim() : null;
  const listPart = viaMatch ? body.slice(0, viaMatch.index) : body;

  // Split on commas that aren't inside parentheses.
  const parts = listPart.split(/,(?![^(]*\))/).map((p) => p.trim()).filter(Boolean);

  const entries = parts.map((part) => {
    const m = part.match(/^([^(]+?)\s*(?:\(([^)]+)\))?$/);
    return m ? { name: m[1].trim(), context: m[2] ?? null } : { name: part, context: null };
  });

  return { entries, via };
}
