(() => {
  const form = document.getElementById('recipe-filter');
  const query = document.getElementById('recipe-query');
  const universe = document.getElementById('recipe-universe');
  const rows = [...document.querySelectorAll('#recipe-table tbody tr')];
  const count = document.getElementById('recipe-count');

  function update() {
    const term = query.value.trim().toLowerCase();
    let visible = 0;
    for (const row of rows) {
      const world = row.cells[3].textContent;
      const matchesUniverse = universe.value === 'All' || world === 'Both' || world === universe.value;
      row.hidden = !matchesUniverse || !row.textContent.toLowerCase().includes(term);
      if (!row.hidden) visible += 1;
    }
    const message = visible === 1 ? '1 reported recipe matches.' : `${visible} reported recipes match.`;
    count.textContent = visible ? `${message} Results are directly below.` : 'No match. Clear filters or check the other universe.';
  }

  form.addEventListener('submit', event => event.preventDefault());
  query.addEventListener('input', update);
  universe.addEventListener('change', update);
  form.addEventListener('reset', () => requestAnimationFrame(update));
})();
