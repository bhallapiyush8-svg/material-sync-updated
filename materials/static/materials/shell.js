(() => {
  let size = 0;
  document.querySelectorAll('[data-font-scale]').forEach(button => {
    button.addEventListener('click', () => {
      const change = Number(button.dataset.fontScale);
      size = change === 0 ? 0 : Math.max(-1, Math.min(2, size + change));
      document.documentElement.style.fontSize = `${16 + size * 2}px`;
    });
  });
  document.querySelectorAll('nav a[href]').forEach(link => {
    const target = new URL(link.href);
    if (target.pathname === location.pathname && !target.hash && target.search === location.search) {
      link.setAttribute('aria-current', 'page');
    }
  });

  document.querySelectorAll('[data-menu-toggle]').forEach(toggle => {
    const menu = document.getElementById(toggle.dataset.menuToggle);
    if (!menu) return;
    toggle.addEventListener('click', () => {
      const open = toggle.getAttribute('aria-expanded') !== 'true';
      toggle.setAttribute('aria-expanded', String(open));
      menu.classList.toggle('is-open', open);
    });
  });

  const sidebar = document.getElementById('workspace-navigation');
  const sidebarToggle = document.querySelector('[data-sidebar-toggle]');
  const backdrop = document.querySelector('[data-sidebar-close]');
  const mobile = window.matchMedia('(max-width: 860px)');
  if (sidebar && sidebarToggle && backdrop) {
    const setSidebar = (open, restoreFocus = false) => {
      document.body.classList.toggle('sidebar-open', open);
      sidebarToggle.setAttribute('aria-expanded', String(open));
      backdrop.hidden = !open;
      sidebar.inert = mobile.matches && !open;
      if (open) sidebar.querySelector('a')?.focus();
      if (!open && restoreFocus) sidebarToggle.focus();
    };
    sidebarToggle.addEventListener('click', () => {
      setSidebar(sidebarToggle.getAttribute('aria-expanded') !== 'true');
    });
    backdrop.addEventListener('click', () => setSidebar(false, true));
    mobile.addEventListener('change', () => setSidebar(false));
    setSidebar(false);
    document.addEventListener('keydown', event => {
      if (!document.body.classList.contains('sidebar-open')) return;
      if (event.key === 'Escape') setSidebar(false, true);
      if (event.key === 'Tab') {
        const links = [...sidebar.querySelectorAll('a[href],button:not([disabled])')];
        const first = links[0], last = links.at(-1);
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault(); last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault(); first?.focus();
        }
      }
    });
  }

  document.querySelectorAll('.login-tabs a').forEach(link => {
    link.addEventListener('click', () => {
      document.querySelectorAll('.login-tabs a').forEach(tab => {
        tab.classList.toggle('active', tab === link);
        if (tab === link) tab.setAttribute('aria-current', 'location');
        else tab.removeAttribute('aria-current');
      });
      const section = document.querySelector(link.hash);
      if (section) {
        section.setAttribute('tabindex', '-1');
        section.focus({preventScroll: true});
      }
    });
  });
  document.querySelector('.password-help-link')?.addEventListener('click', () => {
    const help = document.getElementById('password-help');
    if (help) help.open = true;
  });
})();
