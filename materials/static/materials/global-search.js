(() => {
  document.querySelectorAll('[data-global-search]').forEach(form => {
    const input = form.querySelector('input');
    const popup = form.querySelector('.nav-search-suggestions');
    const results = form.querySelector('[data-search-results]');
    const status = form.querySelector('[data-search-status]');
    let timer, controller, sequence = 0;
    const close = () => { popup.hidden = true; input.setAttribute('aria-expanded', 'false'); };
    input.addEventListener('input', () => {
      clearTimeout(timer); controller?.abort(); const current = ++sequence;
      const query = input.value.trim(); close();
      if (query.length < 2) return;
      timer = setTimeout(async () => {
        controller = new AbortController();
        try {
          const response = await fetch(`${form.dataset.suggestUrl}?q=${encodeURIComponent(query)}`, {signal: controller.signal, credentials: 'same-origin', cache: 'no-store'});
          if (!response.ok) throw new Error('Search unavailable');
          const data = await response.json();
          if (current !== sequence) return;
          results.replaceChildren();
          data.results.forEach(result => {
            const link = document.createElement('a'); link.href = result.url;
            const type = document.createElement('small'); type.textContent = result.type;
            const title = document.createElement('strong'); title.textContent = result.title;
            const context = document.createElement('span'); context.textContent = result.context;
            link.append(type, title, context); results.append(link);
          });
          const all = document.createElement('a'); all.href = `${form.action}?q=${encodeURIComponent(query)}`;
          all.textContent = `View search results for “${query}” →`; results.append(all);
          status.textContent = data.workspace_login_required ? 'Sign in to search workspace records.' : (data.results.length ? '' : 'No matching records.');
          popup.hidden = false; input.setAttribute('aria-expanded', 'true');
        } catch (error) {
          if (error.name === 'AbortError' || current !== sequence) return;
          results.replaceChildren(); status.textContent = 'Suggestions unavailable. Press Enter to search.';
          popup.hidden = false; input.setAttribute('aria-expanded', 'true');
        }
      }, 220);
    });
    form.addEventListener('keydown', event => {
      if (event.key === 'Escape') { close(); input.focus(); }
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        const links = [...results.querySelectorAll('a')]; if (popup.hidden || !links.length) return;
        event.preventDefault();
        const i = links.indexOf(document.activeElement);
        links[event.key === 'ArrowDown' ? (i + 1) % links.length : (i < 1 ? links.length - 1 : i - 1)].focus();
      }
    });
    document.addEventListener('pointerdown', event => { if (!form.contains(event.target)) close(); });
    form.addEventListener('focusout', () => setTimeout(() => { if (!form.contains(document.activeElement)) close(); }, 0));
  });
})();
