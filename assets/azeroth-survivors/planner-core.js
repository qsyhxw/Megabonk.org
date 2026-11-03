/* Reviewed point rules. This module does not simulate damage or edit a game save. */
(function (root) {
  'use strict';
  const empty = (data, classId = 'mage') => ({schema: 1, source: data.source_sha256, classId, budget: 51, sequence: [], name: '', skills: '', gear: '', notes: ''});
  function nodes(data, classId) {
    return (data.classes[classId]?.trees || []).flatMap(tree => tree.nodes.map(node => ({...node, tree: tree.name})));
  }
  const ranks = sequence => sequence.reduce((all, id) => { all[id] = (all[id] || 0) + 1; return all; }, {});
  function addReason(data, plan, id) {
    const list = nodes(data, plan.classId), node = list.find(n => n.id === id), values = ranks(plan.sequence);
    if (!node) return 'This talent is not in the selected class reference.';
    if (plan.sequence.length >= plan.budget) return 'No points remain in this budget. Increase your earned budget or refund a point.';
    if ((values[id] || 0) >= node.max) return node.name + ' is already at its checked rank cap.';
    const treeSpent = plan.sequence.filter(key => list.some(n => n.id === key && n.tree === node.tree)).length;
    if (treeSpent < node.gate) return 'Spend ' + node.gate + ' points in ' + node.tree + ' before buying ' + node.name + '. This point is additional.';
    for (const requirement of node.requires) {
      if ((values[requirement.id] || 0) < requirement.rank) return node.name + ' needs ' + requirement.rank + ' rank(s) in ' + list.find(n => n.id === requirement.id).name + '.';
    }
    if (node.requires_any && !node.requires_any.some(r => (values[r.id] || 0) >= r.rank)) return node.name + ' needs 3 ranks in Soul Devourer or Soul Link.';
    const conflict = node.excludes.find(key => values[key]);
    if (conflict) return node.name + ' excludes ' + list.find(n => n.id === conflict).name + '. Refund that branch first.';
    return '';
  }
  function validate(data, input) {
    if (!input || typeof input !== 'object' || Array.isArray(input) || input.schema !== 1 || input.source !== data.source_sha256) throw Error('Needs verification: this plan belongs to another data snapshot or has an unsupported format. Your current plan was kept.');
    if (!Object.hasOwn(data.classes, input.classId) || !Number.isInteger(input.budget) || input.budget < 0 || input.budget > data.max_points || !Array.isArray(input.sequence) || input.sequence.length > 51) throw Error('Invalid class, point budget or route length. Your current plan was kept.');
    const clean = empty(data, input.classId); clean.budget = input.budget;
    for (const id of input.sequence) {
      if (typeof id !== 'string') throw Error('A talent identifier is invalid.');
      const reason = addReason(data, clean, id); if (reason) throw Error(reason);
      clean.sequence.push(id);
    }
    for (const [key, max] of [['name', 100], ['skills', 800], ['gear', 800], ['notes', 1600]]) {
      if (typeof input[key] !== 'string' || input[key].length > max) throw Error('A plan field is missing or too long: ' + key);
      clean[key] = input[key];
    }
    return clean;
  }
  function add(data, plan, id) {
    const reason = addReason(data, plan, id); if (reason) throw Error(reason);
    return {...plan, sequence: [...plan.sequence, id]};
  }
  function remove(data, plan, id) {
    const index = plan.sequence.lastIndexOf(id); if (index < 0) throw Error('No point in this talent to refund.');
    const sequence = [...plan.sequence]; sequence.splice(index, 1);
    try { return validate(data, {...plan, sequence}); }
    catch { throw Error('Refund blocked: a later point relies on this investment. Remove the dependent point first.'); }
  }
  function example(data, id) {
    const item = data.examples[id]; if (!item) throw Error('Unknown example.');
    return validate(data, {...empty(data, item.classId), ...item});
  }
  const api = {empty, nodes, ranks, addReason, validate, add, remove, example};
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.AzPlanner = api;
})(typeof globalThis !== 'undefined' ? globalThis : this);
