/* Header state, mobile nav, scroll reveal, parallax (hero drift + bands), quick-view dialog */
(function () {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const onScroll = () => header && header.classList.toggle('scrolled', window.scrollY > 24);
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
  }
  // Mark the current page in the nav (lecture pages count as "Content")
  const here = location.pathname.split('/').pop() || 'index.html';
  const inLectures = location.pathname.includes('/lectures/');
  document.querySelectorAll('.nav a').forEach(a => {
    const href = a.getAttribute('href').split('/').pop();
    if (href === here || (inLectures && href === 'content.html')) a.classList.add('active');
  });
  // Reveal on scroll
  const rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px 0px 0px', threshold: 0 });
    rv.forEach(el => io.observe(el));
  } else rv.forEach(el => el.classList.add('in'));

  // Hero drift: the pinned media zooms/drifts slightly as the body covers it
  const media = document.querySelector('.curtain-media[data-parallax]');
  if (media && !reduce) {
    const inner = media.querySelector('.media-inner');
    const tick = () => {
      const y = Math.min(window.scrollY, window.innerHeight);
      if (inner) inner.style.transform = `translateY(${y * 0.18}px) scale(${1 + y / window.innerHeight * 0.06})`;
    };
    tick(); window.addEventListener('scroll', () => requestAnimationFrame(tick), { passive: true });
  }

  // Parallax bands: image drifts against scroll while the band is in view
  const bands = [...document.querySelectorAll('.band')];
  if (bands.length && !reduce) {
    let active = new Set();
    const bio = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? active.add(e.target) : active.delete(e.target)), { rootMargin: '10% 0px' });
    bands.forEach(b => bio.observe(b));
    const move = () => {
      const vh = window.innerHeight;
      active.forEach(b => {
        const r = b.getBoundingClientRect();
        const p = (r.top + r.height / 2 - vh / 2) / (vh / 2 + r.height / 2); // -1 .. 1
        const img = b.querySelector('.band-img');
        if (img) img.style.transform = `translateY(${(-p * 12).toFixed(2)}%)`;
      });
    };
    move(); window.addEventListener('scroll', () => requestAnimationFrame(move), { passive: true });
    window.addEventListener('resize', move);
  }

  // Scroll cue: smooth-scroll to the first content block
  document.querySelectorAll('.scroll-cue a').forEach(a => a.addEventListener('click', ev => {
    const t = document.querySelector(a.getAttribute('href'));
    if (t) { ev.preventDefault(); t.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }
  }));

  // Quick-view dialog for lecture pages (fetches the page and shows its main content)
  const qvLinks = document.querySelectorAll('[data-quickview]');
  if (qvLinks.length && window.HTMLDialogElement) {
    const dlg = document.createElement('dialog'); dlg.className = 'qv';
    dlg.innerHTML = '<div class="qv-head"><a class="btn btn-primary" href="#" target="_self">Open full page</a><button class="qv-close" aria-label="Close"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button></div><div class="qv-body"></div>';
    document.body.appendChild(dlg);
    const body = dlg.querySelector('.qv-body'), open = dlg.querySelector('.qv-head a');
    dlg.querySelector('.qv-close').addEventListener('click', () => dlg.close());
    dlg.addEventListener('click', e => { if (e.target === dlg) dlg.close(); });
    const cache = {};
    qvLinks.forEach(a => a.addEventListener('click', async ev => {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey) return; // let new-tab clicks through
      ev.preventDefault();
      const url = a.getAttribute('href');
      open.setAttribute('href', url);
      body.innerHTML = '<div class="qv-loading">Loading…</div>';
      dlg.showModal(); dlg.scrollTop = 0;
      try {
        if (!cache[url]) {
          const html = await (await fetch(url)).text();
          const doc = new DOMParser().parseFromString(html, 'text/html');
          const main = doc.querySelector('.curtain-body') || doc.querySelector('main');
          const heroCopy = doc.querySelector('.hero-copy .wrap');
          // rewrite relative asset paths for the lecture folder
          const base = url.substring(0, url.lastIndexOf('/') + 1);
          [main, heroCopy].forEach(el => el && el.querySelectorAll('[src],[href]').forEach(n => {
            ['src', 'href'].forEach(attr => { const v = n.getAttribute(attr); if (v && !/^(https?:|mailto:|#|\/)/.test(v)) n.setAttribute(attr, base + v); });
          }));
          cache[url] = (heroCopy ? heroCopy.innerHTML : '') + (main ? main.innerHTML : '');
        }
        body.innerHTML = cache[url];
        body.querySelectorAll('.rv').forEach(el => el.classList.add('in'));
      } catch (e) { body.innerHTML = '<div class="qv-loading">Could not load preview. <a href="' + url + '">Open the page</a>.</div>'; }
    }));
  }
})();
