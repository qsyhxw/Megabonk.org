(() => {
  'use strict';

  const CACHE_PREFIX = 'megabonk:last-known-good:v1:';
  const DEFAULT_MIN_RECORDS = 100;

  function storageKey(url) {
    const pathname = new URL(url, window.location.origin).pathname;
    return `${CACHE_PREFIX}${pathname}`;
  }

  function validate(payload, options = {}) {
    const kind = options.kind || 'leaderboard';
    if (!payload || typeof payload !== 'object') {
      throw new Error('Snapshot payload is not an object');
    }
    if (kind === 'leaderboard') {
      const minimum = options.minRecords ?? DEFAULT_MIN_RECORDS;
      if (!Array.isArray(payload.data) || payload.data.length < minimum) {
        throw new Error(`Leaderboard snapshot contains fewer than ${minimum} records`);
      }
      return payload;
    }
    if (kind === 'leaderboard-meta') {
      if (!Array.isArray(payload.characters) || payload.characters.length === 0) {
        throw new Error('leaderboard-meta snapshot has no character records');
      }
      return payload;
    }
    if (kind === 'character-signals') {
      if (!Array.isArray(payload.characterSignals) || payload.characterSignals.length === 0) {
        throw new Error('character-signals snapshot has no character records');
      }
      return payload;
    }
    throw new Error(`Unknown Megabonk snapshot kind: ${kind}`);
  }

  function remember(url, payload, options) {
    try {
      window.localStorage.setItem(storageKey(url), JSON.stringify({
        savedAt: new Date().toISOString(),
        kind: options.kind || 'leaderboard',
        payload
      }));
    } catch (error) {
      console.warn('Could not save the last-known-good leaderboard snapshot.', error);
    }
  }

  function recall(url, options) {
    try {
      const raw = window.localStorage.getItem(storageKey(url));
      if (!raw) return null;
      const cached = JSON.parse(raw);
      if (cached.kind !== (options.kind || 'leaderboard')) return null;
      validate(cached.payload, options);
      return cached;
    } catch (error) {
      console.warn('Ignoring an invalid cached leaderboard snapshot.', error);
      return null;
    }
  }

  async function load(url, options = {}) {
    const requestUrl = new URL(url, window.location.origin);
    requestUrl.searchParams.set('t', Date.now().toString());
    try {
      const response = await window.fetch(requestUrl.href, { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = validate(await response.json(), options);
      remember(url, payload, options);
      return {
        payload,
        source: 'network',
        isCached: false,
        cachedAt: null,
        warning: null
      };
    } catch (networkError) {
      const cached = recall(url, options);
      if (!cached) throw networkError;
      return {
        payload: cached.payload,
        source: 'cache',
        isCached: true,
        cachedAt: cached.savedAt || null,
        warning: networkError.message || String(networkError)
      };
    }
  }

  function cachedStatus(result) {
    if (!result?.isCached) return '';
    const timestamp = result.cachedAt ? new Date(result.cachedAt) : null;
    const label = timestamp && !Number.isNaN(timestamp.getTime())
      ? timestamp.toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })
      : 'an earlier visit';
    return `Cached last-known-good data · saved ${label}`;
  }

  window.MegabonkLeaderboardData = {
    load,
    validate,
    cachedStatus,
    cachePrefix: CACHE_PREFIX
  };
})();