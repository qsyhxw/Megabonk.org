'use strict';
(() => {
  const normal = s => s.normalize('NFKC').toLocaleLowerCase().trim();
  const search = document.querySelector('#guide-search');
  if (search) {
    const input = document.querySelector('#guide-query'), list = document.querySelector('#guide-results');
    const rows = [...list.children], status = document.querySelector('#guide-status');
    const update = () => {
      const words = normal(input.value).split(/\s+/).filter(Boolean);
      let count = 0;
      for (const row of rows) { row.hidden = !words.every(w => normal(row.dataset.guideSearch).includes(w)); if (!row.hidden) count++; }
      list.hidden = !words.length;
      status.textContent = words.length ? `${count} matching guides${count ? '. Open a result below.' : '. Try a class, system or shorter phrase.'}` : 'Search page names, topics and starting advice. No account or upload.';
    };
    input.addEventListener('input', update); search.addEventListener('submit', e => e.preventDefault());
    search.addEventListener('reset', () => { setTimeout(update, 0); input.focus(); });
  }
  const spellForm = document.querySelector('#spell-filter');
  if (spellForm) {
    const input = document.querySelector('#spell-query'), cls = document.querySelector('#spell-class'), lang = document.querySelector('#spell-language');
    const rows = [...document.querySelectorAll('[data-spell-class]')].map(row => ({row, names: JSON.parse(row.dataset.names)}));
    const update = () => {
      const words = normal(input.value).split(/\s+/).filter(Boolean); let count = 0;
      for (const {row, names} of rows) {
        const hay = normal(Object.values(names).join(' '));
        row.hidden = !!(cls.value && cls.value !== row.dataset.spellClass) || !words.every(w => hay.includes(w));
        row.querySelector('[data-client-name]').textContent = names[lang.value] || names.en;
        if (!row.hidden) count++;
      }
      document.querySelector('#spell-status').textContent = `${count} / ${rows.length} names shown. ${count ? 'English and selected client name appear below.' : 'No match. Reset or try another name.'}`;
    };
    spellForm.addEventListener('input', update); spellForm.addEventListener('change', update);
    spellForm.addEventListener('submit', e => e.preventDefault());
    spellForm.addEventListener('reset', () => { setTimeout(update, 0); input.focus(); }); update();
  }
  const quiz = document.querySelector('#class-finder');
  if (quiz) {
    const tray = document.querySelector('#class-tray'), open = document.querySelector('#class-open'), dialog = document.querySelector('#class-result');
    const values = () => Object.fromEntries(new FormData(quiz));
    quiz.addEventListener('change', () => { const n = Object.keys(values()).length; tray.hidden = !n; open.disabled = n !== 3; document.querySelector('#class-status').textContent = `${n} / 3 chosen`; });
    quiz.addEventListener('submit', e => e.preventDefault());
    quiz.addEventListener('reset', () => { tray.hidden = true; open.disabled = true; if (dialog.open) dialog.close(); });
    open.addEventListener('click', () => {
      const v = values(); if (Object.keys(v).length !== 3) return;
      let slug, why;
      if (v.style === 'summon') { slug = v.progress === 'fresh' ? 'hunter' : 'warlock'; why = v.progress === 'fresh' ? 'Begin with the ranged Hunter opening. A developed pet pair still needs its talents; a fresh hero does not inherit it.' : 'Compare Warlock summon choices and the branch actually allocated. Mutually exclusive demons do not combine into one plan.'; }
      else if (v.style === 'melee') { slug = v.goal === 'survival' ? 'paladin' : 'warrior'; why = slug === 'paladin' ? 'Compare the defensive holy route. Check the current shield and starter milestones before assuming their effects.' : 'Compare Cleave and the supported melee routes. Whirlwind or Mortal Strike openings depend on the chosen talents.'; }
      else { slug = v.goal === 'survival' && v.progress === 'fresh' ? 'hunter' : 'mage'; why = slug === 'hunter' ? 'Use the ranged opening while learning movement; later pet and Aimed Shot benefits need their own investments.' : 'Compare Frost for space control, Fire for kill triggers and Arcane for repeat strikes. Keep the actual starting spell in view.'; }
      const body = document.querySelector('#class-result-body'); body.replaceChildren();
      const title = document.createElement('h3'); title.textContent = slug[0].toUpperCase() + slug.slice(1);
      const text = document.createElement('p'); text.textContent = why;
      const scope = document.createElement('p'); scope.textContent = `${v.progress === 'fresh' ? 'Fresh character' : 'Developed character'}: inspect the picker and current allocation. This shortlist routes preferences to a guide; it does not rank every class or measure win rates.`;
      const link = document.createElement('a'); link.href = `/azeroth-survivors/builds/${slug}/`; link.textContent = 'Open this class route →';
      body.append(title, text, scope, link); dialog.showModal(); document.querySelector('#class-close').focus();
    });
    document.querySelector('#class-close').addEventListener('click', () => dialog.close());
    dialog.addEventListener('close', () => { if (!tray.hidden) open.focus(); });
  }
  const gpu = document.querySelector('#gpu-run');
  if (gpu) gpu.addEventListener('click', async () => {
    const result = document.querySelector('#gpu-result'); gpu.disabled = true; result.textContent = 'Checking this browser…';
    let timer;
    try {
      if (!window.isSecureContext) { result.textContent = 'This page is not a secure context. Open the HTTPS page before checking WebGPU.'; return; }
      if (!navigator.gpu) { result.textContent = 'WebGPU is not exposed here. Inspect browser support and graphics acceleration. This is a local capability result, not a server-status check.'; return; }
      const timeout = Symbol('timeout');
      const adapter = await Promise.race([navigator.gpu.requestAdapter(), new Promise(resolve => { timer = setTimeout(() => resolve(timeout), 8000); })]);
      result.textContent = adapter === timeout ? 'The adapter request did not finish within 8 seconds. Result unknown; retry or inspect browser graphics diagnostics.' : adapter ? 'A WebGPU adapter is available. This does not verify game compatibility, features, stability or performance. If loading still fails, follow the symptom checklist.' : 'WebGPU exists, but no adapter was returned. Inspect graphics acceleration, drivers and the GPU selected for this browser.';
    } catch { result.textContent = 'The browser rejected the adapter check. Result unknown; inspect browser graphics diagnostics. Your game and save were not accessed.'; }
    finally { clearTimeout(timer); gpu.disabled = false; }
  });
})();

