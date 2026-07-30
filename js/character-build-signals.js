(() => {
  'use strict';

  const IMAGE_BASE = '/images/';
  const WEAPON_IMAGES = {
    aura: 'database/weapons/Aura.png', aegis: 'database/weapons/Aegis.png', flamewalker: 'database/weapons/Flamewalker.png',
    frostwalker: 'database/weapons/Frostwalker.png', katana: 'database/weapons/Katana.png', dice: 'database/weapons/Dice.png',
    dexecutioner: 'database/weapons/Dexecutioner.png', bloodmagic: 'database/weapons/Blood_Magic.png', lightningstaff: 'database/weapons/Lightning_Staff.png',
    bananarang: 'database/weapons/Bananarang.png', corruptedsword: 'database/weapons/CorruptedSword.png', bow: 'database/weapons/Bow.png',
    revolver: 'database/weapons/Revolver.png', axe: 'database/weapons/Axe.png', bone: 'database/weapons/Bone.png',
    sniper: 'database/weapons/Sniper.png', blackhole: 'database/weapons/Black_Hole.png', tornado: 'database/weapons/Tornado.png',
    shotgun: 'database/weapons/Shotgun.png', sword: 'database/weapons/Sword.png', herosword: 'database/weapons/Hero_Sword.png',
    firestaff: 'database/weapons/Firestaff.png', chunkers: 'database/weapons/Chunkers.png', spacenoodle: 'database/weapons/Space_Noodle.png',
    dragonsbreath: 'database/weapons/Dragons_Breath.png', sluttyrocket: 'database/weapons/SluttyRocket.png', mines: 'database/weapons/Mines.png',
    poisonflask: 'database/weapons/Poison_Flask.png', wirelessdagger: 'database/weapons/Wireless_Dagger.png', scythe: 'database/weapons/Scythe.png'
  };
  const TOME_IMAGES = {
    agility: 'Tomes/Agility_Tome.png', cooldown: 'Tomes/Cooldown_Tome.png', damage: 'Tomes/Damage_Tome.png',
    evasion: 'Tomes/Evasion_Tome.png', golden: 'Tomes/Golden_Tome.png', health: 'Tomes/Health_Tome.png',
    knockback: 'Tomes/Knockback_Tome.png', precision: 'Tomes/Precision_Tome.png', projectilespeed: 'Tomes/Projectile_Speed_Tome.png',
    regen: 'Tomes/Regen_Tome.png', shield: 'Tomes/Shield_Tome.png', silver: 'Tomes/Silver_Tome.png',
    size: 'Tomes/Size_Tome.png', armor: 'Tomes/Armor_Tome.png', attraction: 'Tomes/Attraction_Tome.png',
    bloody: 'Tomes/Bloody_Tome.png', chaos: 'Tomes/Chaos_Tome.png', cursed: 'Tomes/Cursed_Tome.png',
    duration: 'Tomes/Duration_Tome.png', luck: 'Tomes/Luck_Tome.png', quantity: 'Tomes/Quantity_Tome.png',
    thorns: 'Tomes/Thorns_Tome.png', xp: 'Tomes/XP_Tome.png'
  };
  const NON_BUILD_ITEM_IDS = new Set(['cryptkey']);
  const ITEM_IMAGES = {
    bobslight: '/images/Items/Item_Bobs_Light.png',
    oldmask: '/images/Items/Item_Old_Mask.png',
    pot: '/images/Items/Item_Pot_Stainless_Steel.png',
    wizardshat: '/images/Items/Item_Wizards_Hat.png'
  };
  const WEAPON_ROUTES = {
    aegis: '/database/weapons/aegis', aura: '/database/weapons/aura', axe: '/database/weapons/axe',
    bananarang: '/database/weapons/bananarang', blackhole: '/database/weapons/black-hole', bloodmagic: '/database/weapons/blood-magic',
    bone: '/database/weapons/bone', bow: '/database/weapons/bow', chunkers: '/database/weapons/chunkers',
    corruptedsword: '/database/weapons/corrupted-sword', dexecutioner: '/database/weapons/dexecutioner', dice: '/database/weapons/dice',
    dragonsbreath: '/database/weapons/dragons-breath', firestaff: '/database/weapons/firestaff', flamewalker: '/database/weapons/flamewalker',
    frostwalker: '/database/weapons/frostwalker', herosword: '/database/weapons/hero-sword', katana: '/database/weapons/katana',
    lightningstaff: '/database/weapons/lightning-staff', mines: '/database/weapons/mines', poisonflask: '/database/weapons/poison-flask',
    revolver: '/database/weapons/revolver', scythe: '/database/weapons/scythe', shotgun: '/database/weapons/shotgun',
    sluttyrocket: '/database/weapons/slutty-rocket', sniper: '/database/weapons/sniper-rifle', spacenoodle: '/database/weapons/space-noodle',
    sword: '/database/weapons/sword', tornado: '/database/weapons/tornado', wirelessdagger: '/database/weapons/wireless-dagger'
  };
  const TOME_ROUTES = {
    agility: '/database/tomes/agility-tome', armor: '/database/tomes/armor-tome', attraction: '/database/tomes/attraction-tome',
    bloody: '/database/tomes/bloody-tome', chaos: '/database/tomes/chaos-tome', cooldown: '/database/tomes/cooldown-tome',
    cursed: '/database/tomes/cursed-tome', damage: '/database/tomes/damage-tome', duration: '/database/tomes/duration-tome',
    evasion: '/database/tomes/evasion-tome', golden: '/database/tomes/golden-tome', health: '/database/tomes/health-tome',
    knockback: '/database/tomes/knockback-tome', luck: '/database/tomes/luck-tome', precision: '/database/tomes/precision-tome',
    projectilespeed: '/database/tomes/projectile-speed-tome', quantity: '/database/tomes/quantity-tome', regen: '/database/tomes/regen-tome',
    shield: '/database/tomes/shield-tome', silver: '/database/tomes/silver-tome', size: '/database/tomes/size-tome',
    thorns: '/database/tomes/thorns-tome', xp: '/database/tomes/xp-tome'
  };
  const ITEM_ROUTES = {
    anvil: '/database/items/anvil', backpack: '/database/items/backpack', battery: '/database/items/battery', beacon: '/database/items/beacon',
    beefyring: '/database/items/beefy-ring', beer: '/database/items/beer', bigbonk: '/database/items/big-bonk', bloodycleaver: '/database/items/bloody-cleaver',
    bobdead: '/database/items/bob-dead', bobslight: '/database/items/bobs-light', borgar: '/database/items/borgar', bossbuster: '/database/items/boss-buster', brassknuckles: '/database/items/brass-knuckles',
    cactus: '/database/items/cactus', campfire: '/database/items/campfire', chonkplate: '/database/items/chonkplate', clover: '/database/items/clover',
    cowardscloak: '/database/items/cowards-cloak', creditcardgreen: '/database/items/credit-card-green', creditcardred: '/database/items/credit-card-red',
    curseddoll: '/database/items/cursed-doll', cursedgrabbies: '/database/items/cursed-grabbies', demonicblade: '/database/items/demonic-blade',
    demonicblood: '/database/items/demonic-blood', demonicsoul: '/database/items/demonic-soul', dragonfire: '/database/items/dragonfire',
    eagleclaw: '/database/items/eagle-claw', echoshard: '/database/items/echo-shard', electricplug: '/database/items/electric-plug',
    energycore: '/database/items/energy-core', feathers: '/database/items/feathers', forbiddenjuice: '/database/items/forbidden-juice',
    gamergoggles: '/database/items/gamer-goggles', gasmask: '/database/items/gas-mask', ghost: '/database/items/ghost', giantfork: '/database/items/giant-fork',
    goldenglove: '/database/items/golden-glove', goldenring: '/database/items/golden-ring', goldenshield: '/database/items/golden-shield',
    goldensneakers: '/database/items/golden-sneakers', grandmassecrettonic: '/database/items/grandmas-secret-tonic', gymsauce: '/database/items/gym-sauce',
    holybook: '/database/items/holy-book', icecrystal: '/database/items/ice-crystal', icecube: '/database/items/ice-cube', idlejuice: '/database/items/idle-juice',
    joesdagger: '/database/items/joes-dagger', kevin: '/database/items/kevin', key: '/database/items/key', leechingcrystal: '/database/items/leeching-crystal',
    lightningorb: '/database/items/lightning-orb', medkit: '/database/items/medkit', mirror: '/database/items/mirror', moldycheese: '/database/items/moldy-cheese',
    moldygloves: '/database/items/moldy-gloves', oats: '/database/items/oats', oldmask: '/database/items/old-mask', overpoweredlamp: '/database/items/overpowered-lamp',
    phantomshroud: '/database/items/phantom-shroud', pot: '/database/items/pot-stainless-steel', powergloves: '/database/items/power-gloves',
    quinsmask: '/database/items/quins-mask', scarf: '/database/items/scarf', shatteredknowledge: '/database/items/shattered-knowledge', skuleg: '/database/items/skuleg',
    slipperyring: '/database/items/slippery-ring', slurpgloves: '/database/items/slurp-gloves', sluttycannon: '/database/items/slutty-cannon',
    snek: '/database/items/snek', soulharvester: '/database/items/soul-harvester', speedboi: '/database/items/speed-boi',
    spicymeatball: '/database/items/spicy-meatball', spikyshield: '/database/items/spiky-shield', suckymagnet: '/database/items/sucky-magnet',
    tacticalglasses: '/database/items/tactical-glasses', thundermitts: '/database/items/thunder-mitts', timebracelet: '/database/items/time-bracelet',
    toxicbarrel: '/database/items/toxic-barrel', turboskates: '/database/items/turbo-skates', turbosocks: '/database/items/turbo-socks',
    unstabletransfusion: '/database/items/unstable-transfusion', wizardshat: '/database/items/wizards-hat', wrench: '/database/items/wrench',
    zawarudo: '/database/items/za-warudo'
  };  const LABELS = {
    cl4nk: 'CL4NK', tonymczoom: 'Tony McZoom', siroofie: 'Sir Oofie', sirchadwell: 'Sir Chadwell',
    firestaff: 'Fire Staff', lightningstaff: 'Lightning Staff', bloodmagic: 'Blood Magic', blackhole: 'Black Hole',
    corruptedsword: 'Corrupted Sword', herosword: 'Hero Sword', poisonflask: 'Poison Flask',
    wirelessdagger: 'Wireless Dagger', dragonsbreath: "Dragon's Breath", sluttyrocket: 'Slutty Rocket',
    projectilespeed: 'Projectile Speed', xp: 'XP', cursed: 'Cursed',
    beefyring: 'Beefy Ring', bigbonk: 'Big Bonk', bobslight: "Bob's Light", cowardscloak: "Coward's Cloak",
    creditcardgreen: 'Green Credit Card', creditcardred: 'Red Credit Card', cryptkey: 'Crypt Key', curseddoll: 'Cursed Doll',
    echoshard: 'Echo Shard', electricplug: 'Electric Plug', giantfork: 'Giant Fork', goldenglove: 'Golden Glove',
    goldenshield: 'Golden Shield', grandmassecrettonic: "Grandma's Secret Tonic", gymsauce: 'Gym Sauce', holybook: 'Holy Book',
    icecube: 'Ice Cube', idlejuice: 'Idle Juice', joesdagger: "Joe's Dagger", moldycheese: 'Moldy Cheese', oldmask: 'Old Mask',
    phantomshroud: 'Phantom Shroud', powergloves: 'Power Gloves', slipperyring: 'Slippery Ring', slurpgloves: 'Slurp Gloves',
    sluttycannon: 'Slutty Cannon', soulharvester: 'Soul Harvester', suckymagnet: 'Sucky Magnet', thundermitts: 'Thunder Mitts',
    timebracelet: 'Time Bracelet', unstabletransfusion: 'Unstable Transfusion'  };

  const escapeHtml = value => String(value ?? '').replace(/[&<>'"]/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[char]);
  const formatName = value => LABELS[value] || String(value || 'Unknown')
    .replace(/([a-z0-9])([A-Z])/g, '$1 $2')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, letter => letter.toUpperCase());
  const formatNumber = value => Number(value || 0).toLocaleString('en-US');
  const formatPercent = value => `${Math.round(Number(value || 0) * 100)}%`;
  const formatDate = value => {
    const date = value ? new Date(value) : null;
    return date && !Number.isNaN(date.getTime())
      ? date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
      : 'date not supplied';
  };
  const loadoutKey = entry => [
    ...((entry && entry.weapons) || []).slice().sort(),
    '|',
    ...((entry && entry.tomes) || []).slice().sort()
  ].join(':');

  function renderChips(values, type) {
    const images = type === 'weapon' ? WEAPON_IMAGES : TOME_IMAGES;
    const routes = type === 'weapon' ? WEAPON_ROUTES : TOME_ROUTES;
    const catalogType = type === 'weapon' ? 'weapons' : 'tomes';
    const list = Array.isArray(values) ? values : [];
    if (!list.length) return '<span class="cbs-chip">Not supplied</span>';
    return list.map(value => {
      const shared = window.MegabonkEntities?.get(catalogType, value);
      const image = shared?.image || (images[value] ? `${IMAGE_BASE}${images[value]}` : null);
      const route = shared?.page || routes[value];
      const label = shared?.name || formatName(value);
      const content = `${image ? `<img src="${image}" alt="" width="22" height="22" loading="lazy" decoding="async">` : ''}<span>${escapeHtml(label)}</span>`;
      return route
        ? `<a class="cbs-chip cbs-chip-link" href="${route}" aria-label="View ${escapeHtml(label)} details">${content}</a>`
        : `<span class="cbs-chip">${content}</span>`;
    }).join('');
  }

  function renderItemLinks(values) {
    return values.filter(value => !NON_BUILD_ITEM_IDS.has(value)).map(value => {
      const shared = window.MegabonkEntities?.get('items', value);
      const label = shared?.name || formatName(value);
      const route = shared?.page || ITEM_ROUTES[value];
      const image = shared?.image || ITEM_IMAGES[value] || null;
      const content = `${image ? `<img src="${image}" alt="" width="22" height="22" loading="lazy" decoding="async">` : ''}<span>${escapeHtml(label)}</span>`;
      return route
        ? `<a class="cbs-item-link" href="${route}" aria-label="View ${escapeHtml(label)} details">${content}</a>`
        : `<span class="cbs-item-link is-static">${content}</span>`;
    }).join(' <span aria-hidden="true">&middot;</span> ');
  }

  function cardFromLoadout(loadout, signal) {
    const representative = loadout.representativeRun || {};
    return {
      type: loadout.runs >= 2 ? 'Most repeated' : 'Observed setup',
      title: loadout.runs >= 2 ? 'Most repeated leaderboard loadout' : 'Observed leaderboard loadout',
      meta: loadout.runs >= 2
        ? `${loadout.runs} of ${signal.sampleSize} sampled runs (${formatPercent(loadout.usageRate)})`
        : `Observed in the ${signal.sampleScope}`,
      weapons: loadout.weapons || [],
      tomes: loadout.tomes || [],
      items: representative.items || [],
      key: loadoutKey(loadout)
    };
  }

  function cardFromRun(run, type, title) {
    return {
      type,
      title,
      meta: type === 'Highest score'
        ? `Rank #${formatNumber(run.rank)} · ${formatNumber(run.kills)} kills`
        : `Submitted ${formatDate(run.createdAtIso)} · ${formatNumber(run.kills)} kills`,
      weapons: run.weapons || [],
      tomes: run.tomes || [],
      items: run.items || [],
      key: loadoutKey(run)
    };
  }

  function selectCards(signal) {
    const cards = [];
    const seen = new Set();
    const popular = signal.popularLoadouts && signal.popularLoadouts[0];
    if (popular) {
      const card = cardFromLoadout(popular, signal);
      cards.push(card);
      seen.add(card.key);
    }
    if (signal.sampleSize > 1 && signal.highestScoringRun) {
      const card = cardFromRun(signal.highestScoringRun, 'Highest score', 'Highest-scoring sampled setup');
      if (!seen.has(card.key)) { cards.push(card); seen.add(card.key); }
    }
    if (signal.sampleSize > 1 && signal.mostRecentRun) {
      const card = cardFromRun(signal.mostRecentRun, 'Recently verified', 'Most recently submitted setup');
      if (!seen.has(card.key)) { cards.push(card); seen.add(card.key); }
    }
    for (const loadout of (signal.popularLoadouts || []).slice(1)) {
      if (cards.length >= 3) break;
      const card = cardFromLoadout(loadout, signal);
      if (!seen.has(card.key)) { cards.push(card); seen.add(card.key); }
    }
    return cards.slice(0, 3);
  }

  function renderCard(card) {
    const items = renderItemLinks(card.items.slice(0, 5));
    return `<article class="cbs-card">
      <span class="cbs-card-label">${escapeHtml(card.type)}</span>
      <h3 class="cbs-card-title">${escapeHtml(card.title)}</h3>
      <p class="cbs-card-meta">${escapeHtml(card.meta)}</p>
      <div class="cbs-row"><span class="cbs-row-label">Weapons</span><div class="cbs-chips">${renderChips(card.weapons, 'weapon')}</div></div>
      <div class="cbs-row"><span class="cbs-row-label">Tomes</span><div class="cbs-chips">${renderChips(card.tomes, 'tome')}</div></div>
      ${items ? `<p class="cbs-items"><strong>Representative late-run items:</strong> ${items}</p>` : ''}
    </article>`;
  }

  function confidenceLabel(signal) {
    if (signal.confidence === 'strong') return 'Strong sample';
    if (signal.confidence === 'limited') return 'Limited sample';
    return 'Single-run evidence';
  }

  function render(container, meta, patchState, loadResult) {
    const character = container.dataset.characterBuildSignals;
    const characterEntry = window.MegabonkEntities?.get('characters', character);
    const signal = (meta.characterSignals || []).find(entry => {
      if (entry.character === character) return true;
      const signalEntry = window.MegabonkEntities?.get('characters', entry.character);
      return Boolean(characterEntry && signalEntry && characterEntry.id === signalEntry.id);
    });
    if (!signal) {
      container.innerHTML = '<p class="cbs-empty">No current-version leaderboard Build is available for this character yet. The reviewed guide below remains the primary recommendation.</p>';
      return;
    }

    const cards = selectCards(signal);
    const characterName = characterEntry?.name || formatName(character);
    const sourceVersion = meta.activeVersion || 'unknown';
    const siteVersion = patchState && patchState.latest_version ? patchState.latest_version : null;
    const versionsMatch = !siteVersion || sourceVersion === siteVersion;
    const generatedAt = formatDate(meta.generatedAt);
    const reviewedAt = container.dataset.editorialReviewed || '2026-07-29';
    const characterGuide = characterEntry?.page || '/guides/characters/';
    const guard = versionsMatch
      ? `Version matched: these records use v${escapeHtml(sourceVersion)}. They supplement the reviewed guide; they do not replace it.`
      : `Version guard: leaderboard records currently use v${escapeHtml(sourceVersion)}, while the site tracks v${escapeHtml(siteVersion)}. Treat these as historical performance evidence until the source board accepts the newer patch.`;

    const cacheNotice = loadResult?.isCached ? `<p class="cbs-version-guard">⚠ ${escapeHtml(window.MegabonkLeaderboardData.cachedStatus(loadResult))}. The latest request failed, so this proven snapshot remains visible.</p>` : '';

    container.innerHTML = `${cacheNotice}<div class="cbs-head">
      <div class="cbs-heading">
        <p class="cbs-kicker">Automatically refreshed performance evidence</p>
        <h2 class="cbs-title">Current ${escapeHtml(characterName)} Leaderboard Builds</h2>
        <p class="cbs-intro">Same-version ${escapeHtml(characterName)} runs are analyzed separately, so popular characters do not crowd this sample out. Use these verified outcomes alongside the strategy and progression advice below.</p>
      </div>
      <div class="cbs-badges"><span class="cbs-badge">v${escapeHtml(sourceVersion)}</span><span class="cbs-badge">${signal.sampleSize} sampled runs</span><span class="cbs-badge">${confidenceLabel(signal)}</span></div>
    </div>
    <p class="cbs-version-guard${versionsMatch ? ' is-match' : ''}">${guard}</p>
    <div class="cbs-grid">${cards.map(renderCard).join('')}</div>
    <div class="cbs-usage-note"><strong>How to use this page:</strong> Follow the reviewed weapon, Tome and item priorities first; use the early, mid and late-run sections below to sequence upgrades. Swap only when the alternative improves survival or solves the current map or boss check. For unlocks and passive rules, open the <a href="${escapeHtml(characterGuide)}">${escapeHtml(characterName)} Character Guide</a>.</div>
    <div class="cbs-foot"><span>Snapshot: ${escapeHtml(generatedAt)} · Top ${signal.sampleSize} ${escapeHtml(characterName)} runs. Editorial review: ${escapeHtml(reviewedAt)}. Rankings show successful outcomes, not a guaranteed universal best Build.</span><a href="/leaderboard/builds#${encodeURIComponent(signal.character)}">Analyze leaderboard evidence</a><span class="cbs-source">Leaderboard evidence</span></div>`;

    container.querySelectorAll('img').forEach(image => {
      image.addEventListener('error', () => image.remove(), { once: true });
    });
  }

  async function refreshAll() {
    const containers = [...document.querySelectorAll('[data-character-build-signals]')];
    if (!containers.length) return;
    try {
      await window.MegabonkEntities?.ready;
      const cacheBust = Date.now();
      const [loadResult, patchResponse] = await Promise.all([
        window.MegabonkLeaderboardData.load('/data/character-build-signals.json', { kind: 'character-signals' }),
        fetch(`/data/patch-notes-state.json?t=${cacheBust}`).catch(() => null)
      ]);
      const meta = loadResult.payload;
      const patchState = patchResponse && patchResponse.ok ? await patchResponse.json() : null;
      containers.forEach(container => render(container, meta, patchState, loadResult));
    } catch (error) {
      console.error('Character leaderboard Build signals unavailable:', error);
      containers.forEach(container => {
        container.innerHTML = '<p class="cbs-empty">Live leaderboard evidence is temporarily unavailable. The reviewed Build guide below is unaffected.</p>';
      });
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    refreshAll();
    window.setInterval(refreshAll, 900000);
  });
})();
