/* Season 3 (v0.9.x) public-source extractor for the PokeBonk section.
 *
 * Season 3 moved mechanics out of main-*.js into menus-*.js and changed the base
 * stat formula (physical/special now scale through a share-of-total helper).
 * This adapter loads the public client in a sandboxed page, appends named
 * exports for the reviewed functions/objects (located by structure, then
 * fingerprinted), and writes the League, passives, move runtimes and fusions.
 * Usage: NODE_PATH=<playwright+acorn> node scripts/pokebonk_s3_extract.cjs out.json
 */
const fs = require('node:fs'), crypto = require('node:crypto');
const { inspect, fingerprint } = require('./pokebonk_sync_source.cjs');
const hash = s => crypto.createHash('sha256').update(s).digest('hex');

// Structural locators: each must match exactly one top-level function/var.
const FUNCS = {
  base: s => /maxHp:Math\.round\(/.test(s) && /physical:\w+\(\w+\.atk\)/.test(s),
  runtime: s => /statusChance:\w+,drain:/.test(s),
  archetype: s => /`weather`:\w+\.has\(\w+\.key\)\?`buff`/.test(s),
};
const VARS = {
  passives: s => /^\{[^]*?photosynthesis:\{name:/.test(s),
};

function locate(source) {
  const x = inspect(source), out = {}, fps = {};
  for (const [k, test] of Object.entries(FUNCS)) {
    const hits = x.funcs.filter(f => test(source.slice(f.start, f.end)));
    if (hits.length !== 1) throw Error(`S3 adapter: ${k} matched ${hits.length}`);
    out[k] = hits[0].id.name; fps[k] = fingerprint(hits[0]);
  }
  for (const [k, test] of Object.entries(VARS)) {
    const hits = x.vars.filter(v => v.init && test(source.slice(v.init.start, v.init.end)));
    if (hits.length !== 1) throw Error(`S3 adapter: ${k} matched ${hits.length}`);
    out[k] = hits[0].id.name;
  }
  // Fusions are split over several arrays and combined as [...A,...B,...]; use the combined list.
  const parts = new Set(x.vars.filter(v => v.init && /^\[\{(?:repeats:!0,)?key:`fu-/.test(source.slice(v.init.start, v.init.end))).map(v => v.id.name));
  const combined = x.vars.filter(v => v.init?.type === 'ArrayExpression' && v.init.elements.length > 1 &&
    v.init.elements.every(e => e?.type === 'SpreadElement') && v.init.elements.filter(e => parts.has(e.argument.name)).length >= parts.size);
  if (!parts.size || combined.length !== 1) throw Error(`S3 adapter: fusions (${parts.size} parts, ${combined.length} combined)`);
  out.fusions = combined[0].id.name;
  const db = x.vars.filter(v => v.init?.type === 'NewExpression' && source.slice(v.init.start, v.init.end).includes('`movesByKey`'));
  if (db.length !== 1) throw Error('S3 adapter: database');
  out.db = db[0].id.name;
  return { names: out, fingerprints: fps };
}

async function run(output) {
  const { chromium } = require('playwright');
  const launch = { headless: true };
  if (process.env.PB_PROXY) launch.proxy = { server: process.env.PB_PROXY };
  if (process.env.PB_CHROME_CHANNEL) launch.channel = process.env.PB_CHROME_CHANNEL;
  const browser = await chromium.launch(launch);
  try {
    const ctx = await browser.newContext({ locale: 'en-US', serviceWorkers: 'block' });
    const page = await ctx.newPage();
    const get = async u => { const r = await ctx.request.get(u, { timeout: 60000 }); if (!r.ok()) throw Error('HTTP ' + r.status() + ' ' + u); return r.text(); };
    const version = JSON.parse(await get('https://pokebonk.com/version.json'));
    const html = await get('https://pokebonk.com/?lang=en');
    const entry = html.match(/<script[^>]+src="([^"]*assets\/main-[^"]+)"/);
    if (!entry) throw Error('Missing source entry');
    const mainURL = new URL(entry[1], 'https://pokebonk.com/').href, main = await get(mainURL);
    const menusName = main.match(/menus-[\w-]+\.js/), i18nName = main.match(/i18n-[\w-]+\.js/);
    const langName = (main + await get(new URL(i18nName[0], mainURL).href)).match(/en-[\w-]+\.js/);
    if (!menusName || !i18nName) throw Error('S3 adapter: chunk names');
    const menusURL = new URL(menusName[0], mainURL).href, menus = await get(menusURL);
    const { names, fingerprints } = locate(menus);
    const patched = menus + `\nexport{${Object.entries(names).map(([k, v]) => `${v} as s3_${k}`).join(',')}};`;
    await ctx.route('**/*', r => {
      const u = new URL(r.request().url());
      if (u.origin !== 'https://pokebonk.com') return r.abort();
      if (u.pathname === '/' && r.request().isNavigationRequest())
        return r.fulfill({ contentType: 'text/html', body: '<!doctype html><html lang="en"><head><base href="https://pokebonk.com/"></head><body></body></html>' });
      if (u.pathname === '/assets/s3-inspection.js') return r.fulfill({ contentType: 'application/javascript', body: patched });
      if (u.pathname.startsWith('/assets/') || u.pathname === '/version.json' || /\.json$/.test(u.pathname)) return r.continue();
      return r.abort();
    });
    await page.goto('https://pokebonk.com/?lang=en');
    const extracted = await page.evaluate(async ({ i18n, lang }) => {
      const loc = await import(i18n);
      if (lang) { try { const tr = await import(lang); if (typeof loc.l === 'function') loc.l('en', tr.default); } catch (e) {} }
      const a = await import('/assets/s3-inspection.js');
      await a.s3_db.load();
      const plain = v => JSON.parse(JSON.stringify(v, (k, x) => typeof x === 'function' ? undefined : x));
      const passives = Object.fromEntries(Object.entries(a.s3_passives).map(([k, v]) => [k, { name: typeof v.name === 'function' ? v.name() : v.name, desc: typeof v.desc === 'function' ? v.desc() : v.desc, mods: v.mods || [] }]));
      const moves = {};
      for (const m of a.s3_db.movesByKey.values()) {
        const rt = a.s3_runtime(m.id);
        if (rt) moves[m.key] = { key: m.key, name: m.name, type: m.type, cls: m.cls, dmg: rt.dmg, cd: rt.cd, count: rt.count, area: rt.area, arch: rt.arch, status: rt.status };
      }
      const fusions = a.s3_fusions.map(f => ({ key: f.key, member: f.member, moves: f.moves, kind: f.kind, name: typeof f.name === 'function' ? f.name() : f.name, type: f.type, cls: f.cls }));
      const species = a.s3_db.all.map(x => ({ id: x.id, name: x.name, types: x.types, stats: x.stats, evoFrom: x.evoFrom ?? null, evoLevel: x.evoLevel ?? x.evolutionLevel ?? null, evoMethod: x.evoMethod ?? null }));
      return plain({ passives, moves, fusions, species });
    }, { i18n: new URL(i18nName[0], mainURL).href, lang: langName ? new URL(langName[0], mainURL).href : null });
    const after = JSON.parse(await get('https://pokebonk.com/version.json'));
    if (JSON.stringify(after) !== JSON.stringify(version)) throw Error('Source deployed during collection; retry');
    const result = { schema: 's3-1', observed: version, menus: menusURL, menus_sha256: hash(menus), adapter: names, fingerprints, ...extracted };
    fs.writeFileSync(output, JSON.stringify(result, null, 1) + '\n');
    console.log(JSON.stringify({ observed: version, moves: Object.keys(result.moves).length, fusions: result.fusions.length, passives: Object.keys(result.passives).length, species: result.species.length }));
  } finally { await browser.close(); }
}

module.exports = { locate };
if (require.main === module) run(process.argv[2] || 's3.json').catch(e => { console.error(e.message); process.exit(1); });
