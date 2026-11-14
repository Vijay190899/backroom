/**
 * Word-level diff for a rebuilt sentence: which words of `after` are new compared with
 * `before` (longest common subsequence over whitespace-separated tokens). Used to mark
 * what Backroom changed when the brief is rebuilt; whitespace is kept as its own token.
 */
export function changedWords(before: string, after: string): { text: string; changed: boolean }[] {
  const a = before.split(/(\s+)/);
  const b = after.split(/(\s+)/);
  const lcs: number[][] = Array.from({ length: a.length + 1 }, () => new Array<number>(b.length + 1).fill(0));
  for (let i = a.length - 1; i >= 0; i--) {
    for (let j = b.length - 1; j >= 0; j--) {
      lcs[i][j] = a[i] === b[j] ? lcs[i + 1][j + 1] + 1 : Math.max(lcs[i + 1][j], lcs[i][j + 1]);
    }
  }
  const out: { text: string; changed: boolean }[] = [];
  let i = 0;
  let j = 0;
  while (j < b.length) {
    if (i < a.length && a[i] === b[j]) {
      out.push({ text: b[j], changed: false });
      i++;
      j++;
    } else if (i < a.length && lcs[i + 1][j] >= lcs[i][j + 1]) {
      i++;
    } else {
      out.push({ text: b[j], changed: !/^\s+$/.test(b[j]) });
      j++;
    }
  }
  // Merge neighbours so a changed phrase is one marker, spaces between changed words included.
  const merged: { text: string; changed: boolean }[] = [];
  for (let k = 0; k < out.length; k++) {
    const t = out[k];
    const bridge = /^\s+$/.test(t.text) && out[k - 1]?.changed && out[k + 1]?.changed;
    const changed = t.changed || Boolean(bridge);
    const last = merged.at(-1);
    if (last && last.changed === changed) last.text += t.text;
    else merged.push({ text: t.text, changed });
  }
  return merged;
}
