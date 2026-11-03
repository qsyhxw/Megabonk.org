/* Local drafts and share fragments only. No game save, account or remote build service. */
(() => {
  'use strict';
  const root = document.querySelector('#planner-workbench'); if (!root) return;
  const $ = selector => document.querySelector(selector), C = window.AzPlanner;
  const storageKey = 'az-build-draft-v1';
  const make = (tag, text, cls) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (cls) node.className = cls; return node; };
  let data, plan, activeClass, returnFocus, shareURL = '', drafts = {}, engaged = false;
  const fields = ['name', 'skills', 'gear', 'notes'];
  function say(text, reveal = true) { $('#plan-message').textContent = text; if (reveal) { engaged = true; $('#plan-tray').hidden = false; } }
  function applyPlan(next, message, reveal = true) {
    engaged = reveal;
    plan = C.validate(data, next); activeClass = plan.classId; drafts[activeClass] = plan;
    $('#plan-class').value = activeClass; $('#plan-budget').value = plan.budget;
    for (const field of fields) $('#plan-' + field).value = plan[field];
    buildTrees(); update(); say(message, reveal);
  }
  function buildTrees() {
    const area = $('#planner-trees'); area.replaceChildren();
    for (const tree of data.classes[activeClass].trees) {
      const panel = make('section', undefined, 'talent-tree'), heading = make('h3', tree.name);
      const total = make('output'); total.dataset.treeTotal = tree.name; heading.append(total); panel.append(heading);
      for (const node of tree.nodes) {
        const card = make('div', undefined, 'talent-node'); card.dataset.node = node.id;
        card.append(make('h4', node.name), make('p', node.summary));
        let gate = node.gate ? node.gate + ' points in ' + tree.name + ' first.' : 'Available at 0 points in this tree.';
        const list = C.nodes(data, activeClass);
        if (node.requires.length) gate += ' Needs ' + node.requires.map(r => list.find(n => n.id === r.id).name + ' ' + r.rank + '/' + list.find(n => n.id === r.id).max).join(', ') + '.';
        if (node.requires_any) gate += ' Needs Soul Devourer 3/3 or Soul Link 3/3.';
        if (node.excludes.length) gate += ' Excludes ' + node.excludes.map(id => list.find(n => n.id === id).name).join(', ') + '.';
        card.append(make('p', gate, 'gate'));
        const actions = make('div', undefined, 'talent-buttons'), rank = make('output'); rank.dataset.rank = node.id;
        const minus = make('button', '−'), plus = make('button', '+'); minus.type = plus.type = 'button';
        minus.setAttribute('aria-label', 'Refund point from ' + node.name); plus.setAttribute('aria-label', 'Add point to ' + node.name);
        minus.dataset.refund = node.id; plus.dataset.invest = node.id;
        minus.addEventListener('click', () => change(() => C.remove(data, plan, node.id), 'Refunded one point from ' + node.name + '.'));
        plus.addEventListener('click', () => change(() => C.add(data, plan, node.id), 'Added one point to ' + node.name + '.'));
        actions.append(rank, minus, plus); card.append(actions); panel.append(card);
      }
      area.append(panel);
    }
  }
  function change(action, message) {
    try { plan = action(); drafts[activeClass] = plan; update(); say(message); }
    catch (error) { say(error.message); }
  }
  function update() {
    const values = C.ranks(plan.sequence), list = C.nodes(data, activeClass);
    for (const node of list) {
      const rank = values[node.id] || 0, card = document.querySelector('[data-node="' + node.id + '"]');
      card.classList.toggle('is-picked', rank > 0); card.querySelector('output').textContent = rank + ' / ' + node.max;
      card.querySelector('[data-refund]').disabled = !rank;
      card.querySelector('[data-invest]').disabled = rank === node.max;
    }
    for (const out of document.querySelectorAll('[data-tree-total]')) out.textContent = plan.sequence.filter(id => list.find(n => n.id === id).tree === out.dataset.treeTotal).length + ' pts';
    $('#plan-count').textContent = plan.sequence.length + ' / ' + plan.budget + ' points · ' + (plan.budget - plan.sequence.length) + ' remaining';
    $('#plan-tray').hidden = !engaged;
  }
  function encode(value) { const bytes = new TextEncoder().encode(JSON.stringify(value)); return btoa(Array.from(bytes, b => String.fromCharCode(b)).join('')).replaceAll('+', '-').replaceAll('/', '_').replace(/=+$/, ''); }
  function decode(text) {
    if (text.length > 20000 || !/^[A-Za-z0-9_-]+$/.test(text)) throw Error('Invalid or oversized plan link. Your current plan was kept.');
    const base = text.replaceAll('-', '+').replaceAll('_', '/');
    return JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(Uint8Array.from(atob(base), c => c.charCodeAt(0))));
  }
  function routeGroups() {
    const groups = [], counts = {}, list = C.nodes(data, activeClass);
    plan.sequence.forEach((id, index) => {
      counts[id] = (counts[id] || 0) + 1;
      let group = groups.at(-1);
      if (!group || group.id !== id) { group = {id, start: index + 1, end: index + 1}; groups.push(group); }
      group.end = index + 1; group.rank = counts[id];
    });
    return groups.map(g => (g.start === g.end ? g.start : g.start + '–' + g.end) + ': ' + list.find(n => n.id === g.id).name + ' → rank ' + g.rank + '/' + list.find(n => n.id === g.id).max);
  }
  function openPlan() {
    returnFocus = document.activeElement;
    const area = $('#plan-result'); area.replaceChildren();
    area.append(make('h3', plan.name || data.classes[activeClass].name + ' plan'));
    area.append(make('p', plan.sequence.length + ' / ' + plan.budget + ' points. Rules checked against original v' + data.version + ' on ' + data.checked + '.', 'plan-validation'));
    const list = make('ol', undefined, 'plan-route');
    for (const line of routeGroups()) list.append(make('li', line));
    if (!plan.sequence.length) area.append(make('p', 'No talent points allocated yet. Close this view and add a point in a tree.'));
    else area.append(list);
    for (const [field, title] of [['skills','Skill priorities'],['gear','Equipment checks'],['notes','Run notes']]) {
      if (plan[field]) area.append(make('h3', title), make('pre', plan[field]));
    }
    area.append(make('p', 'This checks recorded point rules, not damage, card availability, unlocks in your account or success in a run. Recheck a different game version.'));
    shareURL = location.origin + location.pathname + '#plan=' + encode(plan); $('#plan-link').value = shareURL;
    $('#plan-share-status').textContent = 'The link contains the plan and any notes you entered. Share only information you want others to read.';
    $('#plan-dialog').showModal(); $('#plan-close').focus();
  }
  async function init() {
    try {
      const response = await fetch('/data/azeroth-planner.json?v=20261103'); if (!response.ok) throw Error('Reference data could not be loaded.');
      data = await response.json(); plan = C.empty(data); activeClass = plan.classId;
      const observed = $('#source-sync');
      if (observed && root.dataset.source !== data.source_sha256) throw Error('The page and reference snapshots differ. Reload before editing.');
      $('#planner-editor').hidden = false; $('#planner-load-status').textContent = 'Ready · Mage and Warlock · checked original v' + data.version;
      const params = new URLSearchParams(location.hash.slice(1));
      if (params.has('plan')) {
        try { plan = C.validate(data, decode(params.get('plan'))); }
        catch (error) { say(error.message); }
      } else if (params.has('example')) {
        try { plan = C.example(data, params.get('example')); } catch (error) { say(error.message); }
      }
      applyPlan(plan, $('#plan-message').textContent || 'Choose a budget you have earned, then add a point.', params.has('plan') || params.has('example'));
      $('#plan-class').addEventListener('change', event => applyPlan(drafts[event.target.value] || C.empty(data, event.target.value), 'Switched class. Each class draft stays in memory while this page is open.'));
      $('#plan-budget').addEventListener('change', event => {
        try { const next = C.validate(data, {...plan, budget: Number(event.target.value)}); plan = next; drafts[activeClass] = plan; update(); say('Budget updated. This is your plan budget, not a reading of your game account.'); }
        catch (error) { event.target.value = plan.budget; say(error.message); }
      });
      for (const field of fields) $('#plan-' + field).addEventListener('input', event => { plan[field] = event.target.value; });
      for (const button of document.querySelectorAll('[data-example]')) button.addEventListener('click', () => applyPlan(C.example(data, button.dataset.example), 'Loaded a 31-point editorial example. Twenty points are left for your own choices.'));
      $('#plan-reset').addEventListener('click', () => applyPlan(C.empty(data, activeClass), 'Current class draft cleared. A separately saved draft is kept until you remove it.'));
      $('#plan-save').addEventListener('click', () => { try { localStorage.setItem(storageKey, JSON.stringify(C.validate(data, plan))); say('Saved one draft in this browser. It is separate from game progress.'); } catch { say('Browser storage is unavailable. Your current plan is still here; use View plan to copy a link or download a JSON file.'); } });
      $('#plan-load').addEventListener('click', () => { try { const saved = localStorage.getItem(storageKey); if (!saved) throw Error('No draft saved in this browser.'); applyPlan(C.validate(data, JSON.parse(saved)), 'Loaded your browser draft.'); } catch (error) { say(error.message || 'Saved draft could not be read.'); } });
      $('#plan-forget').addEventListener('click', () => { try { localStorage.removeItem(storageKey); say('Saved browser draft removed. The open plan is unchanged.'); } catch { say('Browser storage is unavailable; no saved draft was removed.'); } });
      $('#plan-open').addEventListener('click', openPlan); $('#plan-close').addEventListener('click', () => $('#plan-dialog').close());
      $('#plan-dialog').addEventListener('close', () => { if (returnFocus?.isConnected) returnFocus.focus(); });
      $('#plan-copy').addEventListener('click', async () => { try { await navigator.clipboard.writeText(shareURL); $('#plan-share-status').textContent = 'Plan link copied.'; } catch { $('#plan-link').focus(); $('#plan-link').select(); $('#plan-share-status').textContent = 'Select and copy the link above. Your plan has not been uploaded.'; } });
      $('#plan-download').addEventListener('click', () => { const url = URL.createObjectURL(new Blob([JSON.stringify(C.validate(data, plan), null, 2)], {type:'application/json'})); const a = make('a'); a.href = url; a.download = 'azeroth-' + activeClass + '-plan.json'; a.click(); setTimeout(() => URL.revokeObjectURL(url), 1000); });
      $('#plan-upload').addEventListener('change', async event => { const file = event.target.files[0]; if (!file) return; try { if (file.size > 25000) throw Error('This plan file is too large. Choose an exported planner JSON file, not a game save.'); const next = C.validate(data, JSON.parse(await file.text())); applyPlan(next, 'Imported your plan locally. No file was uploaded.'); } catch (error) { say(error.message); } event.target.value = ''; });
      window.addEventListener('hashchange', () => {
        const incoming = new URLSearchParams(location.hash.slice(1));
        try {
          if (incoming.has('plan')) applyPlan(C.validate(data, decode(incoming.get('plan'))), 'Opened the shared plan. Your separately saved browser draft is unchanged.');
          else if (incoming.has('example')) applyPlan(C.example(data, incoming.get('example')), 'Opened the editable example.');
        } catch (error) { say(error.message); }
      });
    } catch (error) { $('#planner-load-status').textContent = 'Planner unavailable: ' + error.message + ' The examples and point-rule explanation below remain readable.'; }
  }
  init();
})();
