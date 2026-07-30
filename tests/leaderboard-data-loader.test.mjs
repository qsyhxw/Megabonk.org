import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../js/leaderboard-data-loader.js', import.meta.url), 'utf8');

function validLeaderboard(count = 100) {
  return { active_version: '1.0.69', data: Array.from({ length: count }, (_, index) => ({ rank: index + 1 })) };
}

function harness(fetchImpl, sharedStore = new Map()) {
  const localStorage = {
    getItem(key) { return sharedStore.has(key) ? sharedStore.get(key) : null; },
    setItem(key, value) { sharedStore.set(key, String(value)); }
  };
  const window = {
    location: { origin: 'https://megabonk.org' },
    localStorage,
    fetch: fetchImpl
  };
  vm.runInNewContext(source, { window, URL, Date, JSON, console });
  return { api: window.MegabonkLeaderboardData, store: sharedStore };
}

test('valid network snapshot is returned and remembered', async () => {
  const payload = validLeaderboard(120);
  const { api, store } = harness(async () => ({ ok: true, json: async () => payload }));
  const result = await api.load('/leaderboard-data.json', { kind: 'leaderboard' });
  assert.equal(result.source, 'network');
  assert.equal(result.isCached, false);
  assert.equal(result.payload.data.length, 120);
  assert.equal(store.size, 1);
});

test('network failure falls back to last-known-good snapshot', async () => {
  const store = new Map();
  const first = harness(async () => ({ ok: true, json: async () => validLeaderboard(130) }), store);
  await first.api.load('/leaderboard-data.json', { kind: 'leaderboard' });
  const offline = harness(async () => { throw new Error('offline'); }, store);
  const result = await offline.api.load('/leaderboard-data.json', { kind: 'leaderboard' });
  assert.equal(result.source, 'cache');
  assert.equal(result.isCached, true);
  assert.equal(result.payload.data.length, 130);
  assert.match(result.warning, /offline/);
  assert.match(offline.api.cachedStatus(result), /Cached last-known-good data/);
});

test('invalid short live snapshot cannot overwrite a valid cached snapshot', async () => {
  const store = new Map();
  const first = harness(async () => ({ ok: true, json: async () => validLeaderboard(140) }), store);
  await first.api.load('/leaderboard-data.json', { kind: 'leaderboard' });
  const before = [...store.values()][0];
  const short = harness(async () => ({ ok: true, json: async () => validLeaderboard(20) }), store);
  const result = await short.api.load('/leaderboard-data.json', { kind: 'leaderboard' });
  assert.equal(result.isCached, true);
  assert.equal(result.payload.data.length, 140);
  assert.equal([...store.values()][0], before);
});

test('metadata snapshots use independent validation and cache keys', async () => {
  const store = new Map();
  const meta = { characters: [{ character: 'fox' }] };
  const { api } = harness(async () => ({ ok: true, json: async () => meta }), store);
  const result = await api.load('/data/leaderboard-meta.json', { kind: 'leaderboard-meta' });
  assert.deepEqual(result.payload, meta);
  assert.equal(store.size, 1);
});

test('failure without a valid cache remains an explicit error', async () => {
  const { api } = harness(async () => { throw new Error('offline'); });
  await assert.rejects(api.load('/leaderboard-data.json', { kind: 'leaderboard' }), /offline/);
});
test('integrated page scripts that use the loader remain valid JavaScript', () => {
  const pages = [
    '../leaderboard/index.html',
    '../leaderboard/builds.html',
    '../leaderboard/today.html',
    '../leaderboard/recent.html',
    '../leaderboard/official.html',
    '../leaderboard/verified.html',
    '../guides/builds/index.html',
    '../guides/characters/character-tier-list/index.html'
  ];
  for (const page of pages) {
    const html = fs.readFileSync(new URL(page, import.meta.url), 'utf8');
    const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi)]
      .map(match => match[1])
      .filter(script => script.includes('MegabonkLeaderboardData'));
    assert.ok(scripts.length > 0, `${page} has a guarded inline consumer`);
    for (const script of scripts) {
      assert.doesNotThrow(() => new Function(script), `${page} inline loader consumer parses`);
    }
  }
});