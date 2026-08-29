/* ==========================================================================
   Interactive neuron network — home hero
   Grey neurons connected by axons. Hovering (or tapping) a neuron fires it;
   the impulse travels as a yellow bolt along its axons to neighbours, which
   fire in turn (with a refractory period) so activity cascades across the
   screen and dies out naturally.
   ========================================================================== */
(function () {
  const canvas = document.getElementById('neurons');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // --- palette ------------------------------------------------------------
  const C = {
    axon: 'rgba(118,127,140,0.20)',
    axonHot: '239,185,60',
    soma: '#c3c8cf',
    somaEdge: '#aab1ba',
    dendrite: 'rgba(150,158,170,0.55)',
    hot: '#f7c948',
    hotCore: '#fff3c4',
  };

  let W = 0, H = 0, dpr = 1;
  let nodes = [], edges = [], impulses = [];
  let mouse = { x: -1e9, y: -1e9 };
  let running = true, last = performance.now(), ambientTimer = 1500;

  // --- helpers ------------------------------------------------------------
  const rand = (a, b) => a + Math.random() * (b - a);
  function qpoint(e, t) { // point along quadratic curve
    const u = 1 - t;
    return {
      x: u * u * e.a.x + 2 * u * t * e.cx + t * t * e.b.x,
      y: u * u * e.a.y + 2 * u * t * e.cy + t * t * e.b.y,
    };
  }

  // --- build network ------------------------------------------------------
  function build() {
    nodes = []; edges = []; impulses = [];
    const spacing = W < 700 ? 82 : W < 1100 ? 100 : 112;
    const cols = Math.ceil(W / spacing) + 2, rows = Math.ceil(H / spacing) + 2;
    for (let r = -1; r < rows; r++) {
      for (let c = -1; c < cols; c++) {
        const x = c * spacing + (r % 2 ? spacing / 2 : 0) + rand(-spacing * .32, spacing * .32);
        const y = r * spacing * 0.9 + rand(-spacing * .3, spacing * .3);
        const dendrites = [];
        const nd = 3 + Math.floor(Math.random() * 3);
        for (let i = 0; i < nd; i++) {
          const ang = rand(0, Math.PI * 2), len = rand(9, 20);
          dendrites.push({ ang, len, branch: Math.random() < .6, bang: rand(-.9, .9), blen: rand(5, 10) });
        }
        nodes.push({ x, y, r: rand(3, 5.2), light: 0, refr: 0, dendrites, nbrs: [] });
      }
    }
    // connect each node to its nearest neighbours
    const maxD = spacing * 1.75;
    const seen = new Set();
    nodes.forEach((n, i) => {
      const cand = [];
      for (let j = 0; j < nodes.length; j++) {
        if (i === j) continue;
        const m = nodes[j], d = Math.hypot(n.x - m.x, n.y - m.y);
        if (d < maxD) cand.push({ j, d });
      }
      cand.sort((p, q) => p.d - q.d);
      const k = 2 + Math.floor(Math.random() * 2);
      cand.slice(0, k).forEach(({ j }) => {
        const key = i < j ? i + '-' + j : j + '-' + i;
        if (seen.has(key)) return;
        seen.add(key);
        const a = n, b = nodes[j];
        const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
        const nx = -(b.y - a.y), ny = (b.x - a.x);
        const nl = Math.hypot(nx, ny) || 1, bend = rand(-0.22, 0.22);
        const e = { a, b, ia: i, ib: j, cx: mx + nx / nl * bend * nl, cy: my + ny / nl * bend * nl, hot: 0, len: Math.hypot(b.x - a.x, b.y - a.y) };
        edges.push(e);
        a.nbrs.push({ e, to: j }); b.nbrs.push({ e, to: i });
      });
    });
  }

  function resize() {
    const rect = canvas.getBoundingClientRect();
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = rect.width; H = rect.height;
    canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    build();
    if (!running) draw();
  }

  // --- firing -------------------------------------------------------------
  function fire(i, from, gen) {
    const n = nodes[i];
    if (n.refr > 0) return;
    n.light = 1; n.refr = 1100; // ms refractory period
    if (reduceMotion) return;
    if (gen > 9) return;
    n.nbrs.forEach(({ e, to }) => {
      if (to === from) return;
      const p = gen === 0 ? 1 : gen < 3 ? 0.92 : gen < 6 ? 0.7 : 0.45;
      if (Math.random() > p) return;
      if (nodes[to].refr > 0) return;
      const forward = e.ia === i; // travel a->b if we're at a
      impulses.push({ e, forward, t: 0, speed: rand(0.9, 1.4) * 260 / e.len, gen: gen + 1, from: i, to });
    });
  }

  function nearest(x, y, maxD) {
    let best = -1, bd = maxD * maxD;
    for (let i = 0; i < nodes.length; i++) {
      const n = nodes[i], d = (n.x - x) ** 2 + (n.y - y) ** 2;
      if (d < bd) { bd = d; best = i; }
    }
    return best;
  }

  // --- update -------------------------------------------------------------
  function update(dt) {
    // hover -> fire
    const hi = nearest(mouse.x, mouse.y, 30);
    if (hi >= 0) fire(hi, -1, 0);

    // ambient spontaneous activity
    if (!reduceMotion) {
      ambientTimer -= dt;
      if (ambientTimer <= 0 && impulses.length < 24) {
        fire(Math.floor(Math.random() * nodes.length), -1, 4);
        ambientTimer = rand(2200, 4800);
      }
    }

    for (const n of nodes) {
      if (n.refr > 0) n.refr -= dt;
      if (n.light > 0) n.light = Math.max(0, n.light - dt / 900);
    }
    for (const e of edges) if (e.hot > 0) e.hot = Math.max(0, e.hot - dt / 700);

    for (let k = impulses.length - 1; k >= 0; k--) {
      const im = impulses[k];
      im.t += im.speed * dt / 1000;
      im.e.hot = Math.max(im.e.hot, 0.9);
      if (im.t >= 1) {
        impulses.splice(k, 1);
        fire(im.to, im.from, im.gen);
      }
    }
  }

  // --- draw ---------------------------------------------------------------
  function draw() {
    ctx.clearRect(0, 0, W, H);

    // axons
    ctx.lineWidth = 1;
    for (const e of edges) {
      ctx.beginPath(); ctx.moveTo(e.a.x, e.a.y); ctx.quadraticCurveTo(e.cx, e.cy, e.b.x, e.b.y);
      ctx.strokeStyle = C.axon; ctx.stroke();
      if (e.hot > 0.01) {
        ctx.strokeStyle = `rgba(${C.axonHot},${(e.hot * 0.55).toFixed(3)})`;
        ctx.lineWidth = 1 + e.hot * 1.2; ctx.stroke(); ctx.lineWidth = 1;
      }
    }

    // neurons
    for (const n of nodes) {
      // dendrites
      ctx.strokeStyle = n.light > 0 ? `rgba(230,175,50,${(0.35 + n.light * .6).toFixed(3)})` : C.dendrite;
      ctx.lineWidth = 1;
      for (const d of n.dendrites) {
        const ex = n.x + Math.cos(d.ang) * d.len, ey = n.y + Math.sin(d.ang) * d.len;
        ctx.beginPath(); ctx.moveTo(n.x + Math.cos(d.ang) * n.r, n.y + Math.sin(d.ang) * n.r); ctx.lineTo(ex, ey); ctx.stroke();
        if (d.branch) {
          ctx.beginPath(); ctx.moveTo(ex, ey);
          ctx.lineTo(ex + Math.cos(d.ang + d.bang) * d.blen, ey + Math.sin(d.ang + d.bang) * d.blen); ctx.stroke();
        }
      }
      // glow
      if (n.light > 0.02) {
        const g = ctx.createRadialGradient(n.x, n.y, 0, n.x, n.y, n.r + 22 * n.light);
        g.addColorStop(0, `rgba(255,214,90,${(0.55 * n.light).toFixed(3)})`);
        g.addColorStop(1, 'rgba(255,214,90,0)');
        ctx.fillStyle = g; ctx.beginPath(); ctx.arc(n.x, n.y, n.r + 22 * n.light, 0, Math.PI * 2); ctx.fill();
      }
      // soma
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      if (n.light > 0.02) {
        const mix = n.light;
        ctx.fillStyle = `rgb(${Math.round(195 + 52 * mix)},${Math.round(200 + 1 * mix)},${Math.round(207 - 135 * mix)})`;
      } else ctx.fillStyle = C.soma;
      ctx.fill();
      ctx.strokeStyle = n.light > 0.02 ? C.hot : C.somaEdge; ctx.lineWidth = 1; ctx.stroke();
    }

    // impulses (bolts)
    for (const im of impulses) {
      const T = im.forward ? im.t : 1 - im.t;
      const dir = im.forward ? 1 : -1;
      // trail
      for (let s = 6; s >= 1; s--) {
        const tt = Math.min(1, Math.max(0, T - dir * s * 0.035));
        const p = qpoint(im.e, tt);
        ctx.beginPath(); ctx.arc(p.x, p.y, 3.2 - s * 0.35, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(247,201,72,${(0.5 - s * 0.07).toFixed(3)})`; ctx.fill();
      }
      const p = qpoint(im.e, T);
      const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, 14);
      g.addColorStop(0, 'rgba(255,240,180,0.95)'); g.addColorStop(0.35, 'rgba(247,201,72,0.6)'); g.addColorStop(1, 'rgba(247,201,72,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, 14, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(p.x, p.y, 2.6, 0, Math.PI * 2); ctx.fillStyle = C.hotCore; ctx.fill();
    }
  }

  function loop(now) {
    if (!running) return;
    const dt = Math.min(50, now - last); last = now;
    update(dt); draw();
    requestAnimationFrame(loop);
  }

  // --- events -------------------------------------------------------------
  function toLocal(ev) {
    const r = canvas.getBoundingClientRect();
    return { x: ev.clientX - r.left, y: ev.clientY - r.top };
  }
  canvas.addEventListener('pointermove', ev => { mouse = toLocal(ev); }, { passive: true });
  canvas.addEventListener('pointerleave', () => { mouse = { x: -1e9, y: -1e9 }; });
  canvas.addEventListener('pointerdown', ev => {
    const p = toLocal(ev); const i = nearest(p.x, p.y, 40);
    if (i >= 0) { nodes[i].refr = 0; fire(i, -1, 0); }
  });
  // Text overlay sits above the canvas; forward its pointer moves too.
  const hero = canvas.parentElement;
  hero.addEventListener('pointermove', ev => { mouse = toLocal(ev); }, { passive: true });
  hero.addEventListener('pointerleave', () => { mouse = { x: -1e9, y: -1e9 }; });

  window.addEventListener('resize', () => { clearTimeout(window.__nrz); window.__nrz = setTimeout(resize, 120); });

  // Pause when the hero is scrolled out of view.
  const io = new IntersectionObserver(entries => {
    const vis = entries[0].isIntersecting;
    if (vis && !running) { running = true; last = performance.now(); requestAnimationFrame(loop); }
    else if (!vis) running = false;
  }, { threshold: 0.02 });
  io.observe(canvas);

  resize();
  // Welcome cascade from a neuron near the centre-left.
  setTimeout(() => { const i = nearest(W * 0.62, H * 0.42, 200); if (i >= 0) fire(i, -1, 0); }, 700);
  requestAnimationFrame(loop);
})();
