/* Header state, mobile nav, scroll reveal, gentle parallax on curtain media */
(function () {
  const header = document.querySelector('.site-header');
  const toggle = document.querySelector('.nav-toggle');
  const nav = document.querySelector('.nav');
  const onScroll = () => header && header.classList.toggle('scrolled', window.scrollY > 24);
  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
  if (toggle && nav) {
    toggle.addEventListener('click', () => {
      const open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.querySelectorAll('a').forEach(a => a.addEventListener('click', () => nav.classList.remove('open')));
  }
  // Mark the current page in the nav
  const here = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === here || (here === '' && href === 'index.html')) a.classList.add('active');
  });
  // Reveal on scroll
  const rv = document.querySelectorAll('.rv');
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { rootMargin: '0px 0px 0px 0px', threshold: 0 });
    rv.forEach(el => io.observe(el));
  } else rv.forEach(el => el.classList.add('in'));
  // Subtle parallax drift of the pinned media as the body scrolls over it
  const media = document.querySelector('.curtain-media[data-parallax]');
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (media && !reduce) {
    const inner = media.querySelector('.media-inner');
    const tick = () => {
      const y = Math.min(window.scrollY, window.innerHeight);
      if (inner) inner.style.transform = `translateY(${y * 0.18}px) scale(${1 + y / window.innerHeight * 0.06})`;
      media.style.setProperty('--fade', Math.min(1, y / (window.innerHeight * 0.9)));
    };
    tick(); window.addEventListener('scroll', () => requestAnimationFrame(tick), { passive: true });
  }
})();
