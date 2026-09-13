(() => {
  const drawer = document.querySelector('#archive-drawer');
  const menu = document.querySelector('.menu-button');
  const current = document.body.dataset.issue;
  const archiveURL = new URL(
    /\/reports\/\d{4}-\d{2}-\d{2}\.html$/.test(location.pathname)
      ? '../archive.json' : './archive.json', location.href);

  let returnURL = location.hash === '#archive-drawer'
    ? location.href.replace(/#.*$/, '') : location.href;

  function closeDrawer(event) {
    event.preventDefault();
    history.replaceState(history.state, '', returnURL);
    syncDrawer();
    menu.focus({preventScroll: true});
  }

  menu.addEventListener('click', event => {
    event.preventDefault();
    returnURL = location.href;
    history.replaceState(history.state, '', '#archive-drawer');
    syncDrawer();
  });
  drawer.querySelector('.drawer-close').addEventListener('click', closeDrawer);
  document.querySelector('.archive-overlay').addEventListener('click', closeDrawer);

  document.body.classList.add('archive-enhanced');

  function syncDrawer() {
    const open = location.hash === '#archive-drawer';
    drawer.classList.toggle('is-open', open);
    drawer.inert = !open;
    menu.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
    if (open) drawer.querySelector('.drawer-close').focus({preventScroll: true});
  }
  addEventListener('hashchange', syncDrawer);
  syncDrawer();
  document.addEventListener('keydown', event => {
    if (location.hash !== '#archive-drawer') return;
    if (event.key === 'Escape') {
      closeDrawer(event);
    }
    if (event.key === 'Tab') {
      const links = [...drawer.querySelectorAll('a[href]')];
      const first = links[0], last = links[links.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    }
  });

  async function refreshArchive() {
    try {
      const response = await fetch(archiveURL, {cache: 'no-store'});
      if (!response.ok) throw new Error('Archive unavailable');
      const dates = await response.json();
      if (!Array.isArray(dates) || !dates.every(day => typeof day === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(day))) {
        throw new Error('Invalid archive');
      }
      const fragment = document.createDocumentFragment();
      let year, list;
      for (const day of [...new Set(dates)].sort().reverse()) {
        if (year !== day.slice(0, 4)) {
          year = day.slice(0, 4);
          const section = document.createElement('section');
          const heading = document.createElement('h2');
          heading.className = 'archive-year'; heading.textContent = year;
          list = document.createElement('ul'); list.className = 'archive-dates';
          section.append(heading, list); fragment.append(section);
        }
        const li = document.createElement('li');
        const link = document.createElement('a');
        link.href = new URL(`reports/${day}.html`, archiveURL).href;
        link.textContent = day.slice(5).replace('-', '.');
        if (day === current) link.setAttribute('aria-current', 'page');
        li.append(link); list.append(li);
      }
      document.querySelector('.archive-list').replaceChildren(fragment);
    } catch {
      // The current-issue fallback remains usable when offline or opened via file://.
    }
  }
  refreshArchive();
  addEventListener('pageshow', refreshArchive);
})();
