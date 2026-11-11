export const THEME_STORAGE_KEY = "backroom-theme";

/** Runs before first paint (inline in <head>) so the page never flashes the wrong theme. */
export const themeInitScript = `(function(){try{var t=localStorage.getItem("${THEME_STORAGE_KEY}");var d=t?t==="dark":matchMedia("(prefers-color-scheme: dark)").matches;document.documentElement.classList.toggle("dark",d)}catch(e){}})()`;

const listeners = new Set<() => void>();

export function subscribeTheme(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function isDark(): boolean {
  return document.documentElement.classList.contains("dark");
}

export function setDark(dark: boolean): void {
  document.documentElement.classList.toggle("dark", dark);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, dark ? "dark" : "light");
  } catch {
    // Private mode: the choice simply lasts for this page view.
  }
  listeners.forEach((listener) => listener());
}
