/* Local-only progressive enhancement. Tables work without JavaScript. */
(() => {
  'use strict';
  document.querySelectorAll('[data-reference]').forEach(box => {
    const input = box.querySelector('input'), rows = [...box.querySelectorAll('tbody tr')], result = box.querySelector('[data-result]');
    input.addEventListener('input', () => {
      const words = input.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let visible = 0;
      rows.forEach(row => {
        const text = row.textContent.toLocaleLowerCase();
        row.hidden = !words.every(word => text.includes(word));
        if (!row.hidden) visible++;
      });
      result.textContent = `${visible} of ${rows.length} rows`;
    });
  });
  const a = document.getElementById('move-a'), b = document.getElementById('move-b');
  if (a && b) {
    const recipes = [...document.querySelectorAll('[data-fusion]')].map(e => JSON.parse(e.dataset.fusion));
    const output = document.getElementById('fusion-answer');
    const match = () => {
      if (!a.value || !b.value) { output.textContent = 'Select two different listed kit moves.'; return; }
      if (a.value === b.value) { output.textContent = 'Choose two different moves; a move cannot fill both ingredient slots.'; return; }
      const ta = a.selectedOptions[0].dataset.type, tb = b.selectedOptions[0].dataset.type;
      let result = recipes.find(r => r.kind === 'signature' && r.moves.includes(a.value) && r.moves.includes(b.value));
      result ||= recipes.find(r => r.kind === 'reaction' && ((r.pair[0].includes(ta) && r.pair[1].includes(tb)) || (r.pair[0].includes(tb) && r.pair[1].includes(ta))));
      result ||= ta === tb && recipes.find(r => r.kind === 'type' && r.type === ta);
      result ||= recipes.find(r => r.kind === 'glitch');
      output.textContent = `${result.name} — ${result.kind}. Each eligible ingredient still needs level 8 in your run.`;
    };
    a.addEventListener('change', match); b.addEventListener('change', match);
  }
})();
