
const STORAGE_KEY = 'sp_theme';

export function getTheme() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === 'light' || saved === 'dark') return saved;
  } catch { /* storage may be unavailable */ }
  return 'dark';
}

export function applyTheme(theme) {
  const t = theme === 'light' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', t);
  try { localStorage.setItem(STORAGE_KEY, t); } catch { /* ignore */ }
  return t;
}

export function toggleTheme() {
  const next = getTheme() === 'light' ? 'dark' : 'light';
  return applyTheme(next);
}

export function initTheme() {
  applyTheme(getTheme());
}
