(() => {
  'use strict';

  const normalize = value => String(value || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  let indexes = null;

  function buildIndexes(payload) {
    const result = {};
    for (const [type, entries] of Object.entries(payload.entities || {})) {
      const index = new Map();
      for (const entry of entries) {
        for (const key of [entry.id, entry.name, ...(entry.aliases || [])]) {
          index.set(normalize(key), entry);
        }
      }
      result[type] = index;
    }
    return result;
  }

  const ready = fetch('/data/entity-catalog.json', { cache: 'no-cache' })
    .then(response => {
      if (!response.ok) throw new Error(`Entity catalog returned ${response.status}`);
      return response.json();
    })
    .then(payload => {
      indexes = buildIndexes(payload);
      return payload;
    });

  function get(type, value) {
    return indexes?.[type]?.get(normalize(value)) || null;
  }

  window.MegabonkEntities = {
    ready,
    get,
    normalize,
    name(type, value) {
      return get(type, value)?.name || null;
    },
    image(type, value) {
      return get(type, value)?.image || null;
    },
    page(type, value) {
      return get(type, value)?.page || null;
    },
  };
})();
