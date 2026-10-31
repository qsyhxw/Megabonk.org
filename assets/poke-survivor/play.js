/* Keep one cross-origin frame alive while switching between play and reading. */
(() => {
  'use strict';
  const panel = document.getElementById('game-panel');
  if (!panel) return;
  const frame = document.getElementById('game-frame');
  const expand = document.getElementById('game-expand');
  const minimize = document.getElementById('game-minimize');
  const restore = document.getElementById('game-restore');
  const dock = document.getElementById('game-dock');
  const status = document.getElementById('game-status');
  const background = [...document.querySelectorAll('[data-play-background], body > .top, body > .footer, body > .skip')];
  let started = false;
  let mode = 'normal';
  function setMode(next) {
    const wasExpanded = mode === 'expanded';
    mode = next;
    panel.dataset.mode = next;
    dock.hidden = next !== 'minimized';
    expand.textContent = next === 'expanded' ? 'Exit expanded view' : 'Expand game';
    expand.setAttribute('aria-pressed', String(next === 'expanded'));
    minimize.setAttribute('aria-expanded', String(next !== 'minimized'));
    document.body.classList.toggle('game-expanded', next === 'expanded');
    document.body.classList.toggle('game-minimized', next === 'minimized');
    background.forEach(node => { node.inert = next === 'expanded'; });
    if (wasExpanded && next === 'normal') panel.scrollIntoView({ block: 'start', behavior: 'instant' });
  }
  document.getElementById('game-launch').addEventListener('click', () => {
    if (started) return;
    started = true;
    frame.src = frame.dataset.src;
    frame.hidden = false;
    document.getElementById('game-cover').hidden = true;
    expand.disabled = false;
    minimize.disabled = false;
    status.textContent = 'Connecting to pokesurvivor.pro. Wait for its game menu.';
    expand.focus({ preventScroll: true });
  });
  frame.addEventListener('load', () => {
    if (started) status.textContent = 'The window loaded. Game resources may still be starting; check the menu inside.';
  });
  expand.addEventListener('click', () => setMode(mode === 'expanded' ? 'normal' : 'expanded'));
  minimize.addEventListener('click', () => { setMode('minimized'); restore.focus(); });
  restore.addEventListener('click', () => {
    setMode('normal');
    panel.scrollIntoView({ block: 'start', behavior: 'instant' });
    expand.focus({ preventScroll: true });
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mode === 'expanded') { setMode('normal'); expand.focus({ preventScroll: true }); }
  });
})();
