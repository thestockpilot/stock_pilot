
const cache = new Map();
const subscribers = new Map(); // key -> Set<callback>

export function getCached(key, maxAgeMs = 30000) {
  const entry = cache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.ts > maxAgeMs) {
    cache.delete(key);
    return null;
  }
  return entry.data;
}

export function setCache(key, data) {
  cache.set(key, { data, ts: Date.now() });
  const subs = subscribers.get(key);
  if (subs) {
    for (const cb of subs) {
      try { cb(data); } catch { /* a bad subscriber must not break the others */ }
    }
  }
}

export function clearCache(keyPrefix) {
  if (!keyPrefix) { cache.clear(); return; }
  for (const k of cache.keys()) {
    if (k.startsWith(keyPrefix)) cache.delete(k);
  }
}

export function subscribe(key, callback) {
  let set = subscribers.get(key);
  if (!set) { set = new Set(); subscribers.set(key, set); }
  set.add(callback);
  return () => {
    const s = subscribers.get(key);
    if (s) { s.delete(callback); if (s.size === 0) subscribers.delete(key); }
  };
}
