/**
 * Aura MediX — Premium Ambient Particle System v6.0
 * Layered depth · Mouse parallax · Neural web · Breathing nodes
 * Performance-first: RAF-throttled, GPU-composited, off-screen aware
 */
(function () {
  'use strict';

  /* ── Canvas Setup ───────────────────────────────────────────────────── */
  const canvas = document.getElementById('app-particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d', { alpha: true });

  let W, H, dpr;
  let mouse = { x: -9999, y: -9999 };
  let rafId = null;
  let lastTime = 0;
  const TARGET_FPS = 50;
  const FRAME_MS = 1000 / TARGET_FPS;

  function resize() {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = window.innerWidth;
    H = window.innerHeight;
    canvas.width  = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width  = W + 'px';
    canvas.style.height = H + 'px';
    ctx.scale(dpr, dpr);
  }

  /* ── Color Palette — purple-dominant, no harsh neon ─────────────────── */
  const PALETTE = [
    { r: 124, g: 58,  b: 237 }, // violet-600
    { r: 147, g: 51,  b: 234 }, // violet-500
    { r: 167, g: 139, b: 250 }, // violet-400 (soft)
    { r: 96,  g: 165, b: 250 }, // blue-400 (accent)
    { r: 236, g: 72,  b: 153 }, // pink-500 (rare)
    { r: 199, g: 120, b: 255 }, // lavender
  ];

  function col(c, a) {
    return `rgba(${c.r},${c.g},${c.b},${a.toFixed(3)})`;
  }

  /* ── Particle Factory ────────────────────────────────────────────────── */
  const LAYERS = [
    { count: 22, rMin: 0.8, rMax: 1.6, speed: 0.12, lineLen: 110, lineOpacity: 0.07, depth: 0.3 },
    { count: 18, rMin: 1.2, rMax: 2.2, speed: 0.20, lineLen: 140, lineOpacity: 0.09, depth: 0.6 },
    { count: 12, rMin: 1.8, rMax: 3.0, speed: 0.28, lineLen: 160, lineOpacity: 0.10, depth: 1.0 },
  ];

  const pools = [];

  class Particle {
    constructor(layer) {
      this.layer = layer;
      this.reset(true);
    }

    reset(init) {
      const l = this.layer;
      this.x    = init ? Math.random() * W : (Math.random() < 0.5 ? -10 : W + 10);
      this.y    = Math.random() * H;
      const angle = Math.random() * Math.PI * 2;
      const spd   = (Math.random() * 0.5 + 0.5) * l.speed;
      this.vx   = Math.cos(angle) * spd;
      this.vy   = Math.sin(angle) * spd;
      this.r    = Math.random() * (l.rMax - l.rMin) + l.rMin;
      this.a    = Math.random() * 0.35 + 0.10;
      this.c    = PALETTE[Math.floor(Math.random() * PALETTE.length)];
      this.life = 0;
      this.maxLife = Math.random() * 600 + 400;
      // slow drift oscillation
      this.driftAmp   = Math.random() * 0.04 + 0.01;
      this.driftPhase = Math.random() * Math.PI * 2;
      this.driftFreq  = Math.random() * 0.002 + 0.001;
      // pulse
      this.pulsePhase = Math.random() * Math.PI * 2;
      this.pulseFreq  = Math.random() * 0.015 + 0.005;
    }

    update(t) {
      const l = this.layer;
      // Drift
      this.vx += Math.sin(t * this.driftFreq + this.driftPhase) * this.driftAmp * 0.01;
      this.vy += Math.cos(t * this.driftFreq + this.driftPhase) * this.driftAmp * 0.01;

      // Very gentle mouse attraction (barely perceptible — premium feel)
      const dx = mouse.x - this.x;
      const dy = mouse.y - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 220 && dist > 0) {
        const strength = (1 - dist / 220) * 0.00012 * l.depth;
        this.vx += (dx / dist) * strength;
        this.vy += (dy / dist) * strength;
      }

      // Speed cap
      const spd = Math.sqrt(this.vx * this.vx + this.vy * this.vy);
      const maxSpd = l.speed * 2.5;
      if (spd > maxSpd) { this.vx *= maxSpd / spd; this.vy *= maxSpd / spd; }

      this.x += this.vx;
      this.y += this.vy;
      this.life++;

      // OOB reset
      if (
        this.x < -30 || this.x > W + 30 ||
        this.y < -30 || this.y > H + 30 ||
        this.life > this.maxLife
      ) this.reset();
    }

    draw(t) {
      const fade = Math.min(this.life / 60, 1 - Math.max(0, this.life - this.maxLife + 60) / 60);
      const pulse = 0.85 + 0.15 * Math.sin(t * this.pulseFreq + this.pulsePhase);
      const alpha = this.a * fade * pulse;
      if (alpha < 0.005) return;

      ctx.save();
      // Soft glow
      ctx.shadowColor = col(this.c, 0.5);
      ctx.shadowBlur  = this.r * 5 * this.layer.depth;
      ctx.globalAlpha = alpha;
      ctx.fillStyle   = col(this.c, 1);
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    }
  }

  /* ── Breathing Nodes (large, ultra-soft) ────────────────────────────── */
  const NODES = [];
  const NODE_COUNT = 5;
  class BreathNode {
    constructor(i) {
      this.x     = (W / (NODE_COUNT + 1)) * (i + 1) + (Math.random() - 0.5) * 200;
      this.y     = H * (0.25 + Math.random() * 0.5);
      this.r     = Math.random() * 80 + 60;
      this.phase = Math.random() * Math.PI * 2;
      this.freq  = 0.0008 + Math.random() * 0.0005;
      this.c     = PALETTE[Math.floor(Math.random() * 3)]; // purple-only
      this.vx    = (Math.random() - 0.5) * 0.04;
      this.vy    = (Math.random() - 0.5) * 0.03;
    }
    update() {
      this.x += this.vx; this.y += this.vy;
      if (this.x < 0 || this.x > W) this.vx *= -1;
      if (this.y < 0 || this.y > H) this.vy *= -1;
    }
    draw(t) {
      const pulse = 0.85 + 0.15 * Math.sin(t * this.freq + this.phase);
      const alpha = 0.025 * pulse;
      const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * pulse);
      gradient.addColorStop(0,   col(this.c, alpha * 3));
      gradient.addColorStop(0.5, col(this.c, alpha));
      gradient.addColorStop(1,   col(this.c, 0));
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r * pulse, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const NODE_POINTS = [];
  const NODE_POINT_COUNT = 6;

  class GlowNode {
    constructor(i) {
      this.x     = W * (0.16 + (i / NODE_POINT_COUNT) * 0.68) + (Math.random() - 0.5) * 90;
      this.y     = H * (0.18 + (i % 2) * 0.36) + (Math.random() - 0.5) * 75;
      this.r     = Math.random() * 18 + 22;
      this.phase = Math.random() * Math.PI * 2;
      this.freq  = 0.0009 + Math.random() * 0.0006;
      this.c     = PALETTE[Math.floor(Math.random() * 4)];
      this.vx    = (Math.random() - 0.5) * 0.03;
      this.vy    = (Math.random() - 0.5) * 0.02;
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      if (this.x < 0 || this.x > W) this.vx *= -1;
      if (this.y < 0 || this.y > H) this.vy *= -1;
    }
    draw(t) {
      const pulse = 0.92 + 0.14 * Math.sin(t * this.freq + this.phase);
      const alpha = 0.12 * pulse;
      const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.r * 1.5 * pulse);
      gradient.addColorStop(0, col(this.c, alpha * 1.4));
      gradient.addColorStop(0.35, col(this.c, alpha * 0.55));
      gradient.addColorStop(1, col(this.c, 0));
      ctx.fillStyle = gradient;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r * pulse * 1.4, 0, Math.PI * 2);
      ctx.fill();

      ctx.save();
      ctx.globalAlpha = 0.18 * pulse;
      ctx.strokeStyle = col(this.c, 0.82);
      ctx.lineWidth = 1.2;
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.r * 2.2, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }
  }

  function drawNodeLinks(nodes, maxDist, maxOpacity) {
    const len = nodes.length;
    for (let i = 0; i < len; i++) {
      for (let j = i + 1; j < len; j++) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d  = dx * dx + dy * dy;
        if (d > maxDist * maxDist) continue;
        const dist = Math.sqrt(d);
        const t = 1 - dist / maxDist;
        const alpha = maxOpacity * t * t;
        if (alpha < 0.008) continue;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.strokeStyle = `rgba(167,139,250,1)`;
        ctx.lineWidth = 0.8;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  /* ── Connection Lines ────────────────────────────────────────────────── */
  function drawConnections(particles, maxDist, maxOpacity) {
    const len = particles.length;
    for (let i = 0; i < len; i++) {
      for (let j = i + 1; j < len; j++) {
        const a = particles[i], b = particles[j];
        const dx = b.x - a.x, dy = b.y - a.y;
        const d  = dx * dx + dy * dy;
        if (d > maxDist * maxDist) continue;
        const dist = Math.sqrt(d);
        const t    = 1 - dist / maxDist;
        const alpha = maxOpacity * t * t; // quadratic falloff
        if (alpha < 0.005) continue;
        ctx.save();
        ctx.globalAlpha = alpha;
        ctx.strokeStyle = `rgba(167,139,250,1)`;
        ctx.lineWidth   = 0.6;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  /* ── Scanline shimmer (single horizontal band, very subtle) ─────────── */
  let shimmerY = -80;
  function drawScanShimmer(t) {
    shimmerY += 0.35;
    if (shimmerY > H + 80) shimmerY = -80;
    const grad = ctx.createLinearGradient(0, shimmerY - 40, 0, shimmerY + 40);
    grad.addColorStop(0,   'rgba(167,139,250,0)');
    grad.addColorStop(0.5, 'rgba(167,139,250,0.018)');
    grad.addColorStop(1,   'rgba(167,139,250,0)');
    ctx.fillStyle = grad;
    ctx.fillRect(0, shimmerY - 40, W, 80);
  }

  /* ── Init ────────────────────────────────────────────────────────────── */
  function init() {
    resize();
    pools.length = 0;
    NODES.length = 0;
    NODE_POINTS.length = 0;
    LAYERS.forEach(layer => {
      const group = [];
      for (let i = 0; i < layer.count; i++) group.push(new Particle(layer));
      pools.push({ layer, particles: group });
    });
    for (let i = 0; i < NODE_COUNT; i++) NODES.push(new BreathNode(i));
    for (let i = 0; i < NODE_POINT_COUNT; i++) NODE_POINTS.push(new GlowNode(i));
  }

  /* ── Render Loop ─────────────────────────────────────────────────────── */
  function frame(now) {
    rafId = requestAnimationFrame(frame);
    const delta = now - lastTime;
    if (delta < FRAME_MS) return;
    lastTime = now - (delta % FRAME_MS);

    ctx.clearRect(0, 0, W, H);

    const t = now * 0.001;

    // Breathing nodes (behind everything)
    NODES.forEach(n => { n.update(); n.draw(t); });

    // Glow node web and anchor points
    NODE_POINTS.forEach(node => node.update());
    drawNodeLinks(NODE_POINTS, 240, 0.08);
    NODE_POINTS.forEach(node => node.draw(t));

    // Connections per layer
    pools.forEach(({ layer, particles }) => {
      drawConnections(particles, layer.lineLen, layer.lineOpacity);
    });

    // Particles
    pools.forEach(({ particles }) => {
      particles.forEach(p => { p.update(t); p.draw(t); });
    });

    // Scan shimmer
    drawScanShimmer(t);
  }

  /* ── Visibility API — pause when tab hidden ──────────────────────────── */
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      if (rafId) { cancelAnimationFrame(rafId); rafId = null; }
    } else {
      lastTime = performance.now();
      rafId = requestAnimationFrame(frame);
    }
  });

  /* ── Pointer ─────────────────────────────────────────────────────────── */
  document.addEventListener('mousemove', e => { mouse.x = e.clientX; mouse.y = e.clientY; });
  document.addEventListener('mouseleave', () => { mouse.x = -9999; mouse.y = -9999; });

  /* ── Resize (debounced) ──────────────────────────────────────────────── */
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      resize();
      NODES.length = 0;
      NODE_POINTS.length = 0;
      for (let i = 0; i < NODE_COUNT; i++) NODES.push(new BreathNode(i));
      for (let i = 0; i < NODE_POINT_COUNT; i++) NODE_POINTS.push(new GlowNode(i));
    }, 200);
  });

  /* ── Boot ────────────────────────────────────────────────────────────── */
  init();
  rafId = requestAnimationFrame(frame);

})();