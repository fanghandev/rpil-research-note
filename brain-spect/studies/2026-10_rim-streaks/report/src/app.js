// Interactive layer for the report HTML: contents tools and scroll-spy, collapsible
// sections, click-to-zoom figures, sortable tables. No network access needed.
(function () {
  const toc = document.getElementById('TOC');
  const sections = Array.from(document.querySelectorAll('section.level1, section.level2'));

  // contents tools: expand / collapse all, PDF, print
  if (toc) {
    const tools = document.createElement('div');
    tools.className = 'toc-tools';
    const button = (label, fn) => {
      const b = document.createElement('button');
      b.textContent = label;
      b.addEventListener('click', fn);
      tools.appendChild(b);
    };
    button('Expand all', () => sections.forEach(s => s.classList.remove('collapsed')));
    button('Collapse all', () => sections.forEach(s => s.classList.add('collapsed')));
    const pdf = document.createElement('a');
    pdf.href = 'report.pdf';
    pdf.textContent = 'PDF';
    tools.appendChild(pdf);
    button('Print', () => window.print());
    toc.prepend(tools);
  }

  // collapsible sections: click a heading to fold its section
  sections.forEach(s => {
    const h = s.querySelector(':scope > h1, :scope > h2');
    if (!h) return;
    h.classList.add('collapsible');
    h.title = 'Click to fold or unfold this section';
    h.addEventListener('click', () => s.classList.toggle('collapsed'));
  });

  // opening a contents link unfolds the target and its parents
  if (toc) {
    toc.addEventListener('click', e => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      let el = document.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
      while (el) {
        if (el.classList && el.classList.contains('collapsed')) el.classList.remove('collapsed');
        el = el.parentElement;
      }
    });
  }

  // scroll-spy: mark the contents entry of the section in view
  const links = toc ? Array.from(toc.querySelectorAll('a[href^="#"]')) : [];
  const byId = new Map(links.map(a => [decodeURIComponent(a.getAttribute('href').slice(1)), a]));
  const spy = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      const a = byId.get(en.target.id);
      if (!a) return;
      links.forEach(l => l.classList.remove('active'));
      a.classList.add('active');
    });
  }, { rootMargin: '0px 0px -75% 0px' });
  sections.forEach(s => s.id && spy.observe(s));

  // click-to-zoom figures
  const box = document.createElement('div');
  box.id = 'lightbox';
  const big = document.createElement('img');
  box.appendChild(big);
  document.body.appendChild(box);
  box.addEventListener('click', () => box.classList.remove('open'));
  document.addEventListener('keydown', e => { if (e.key === 'Escape') box.classList.remove('open'); });
  document.querySelectorAll('figure img').forEach(img => {
    img.addEventListener('click', () => {
      big.src = img.src;
      big.alt = img.alt;
      box.classList.add('open');
    });
  });

  // sortable tables: click a header cell
  const key = t => {
    const n = parseFloat(t.replace(/[^0-9.\-−]/g, '').replace('−', '-'));
    return isNaN(n) ? t.toLowerCase() : n;
  };
  document.querySelectorAll('table').forEach(table => {
    const head = table.querySelectorAll('thead th');
    const body = table.querySelector('tbody');
    if (!body) return;
    head.forEach((th, col) => {
      th.title = 'Click to sort';
      th.addEventListener('click', () => {
        const asc = !th.classList.contains('sorted-asc');
        head.forEach(h => h.classList.remove('sorted-asc', 'sorted-desc'));
        th.classList.add(asc ? 'sorted-asc' : 'sorted-desc');
        const rows = Array.from(body.rows);
        rows.sort((a, b) => {
          const x = key(a.cells[col].textContent), y = key(b.cells[col].textContent);
          return (x > y ? 1 : x < y ? -1 : 0) * (asc ? 1 : -1);
        });
        rows.forEach(r => body.appendChild(r));
      });
    });
  });
})();
