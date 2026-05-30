/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Landing Page JS
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Navbar scroll effect ─────────────────────────────────────────────── */
const lNav = document.getElementById('lNav');
window.addEventListener('scroll', () => {
  lNav.classList.toggle('scrolled', window.scrollY > 40);
}, { passive: true });

/* ── Mobile menu ──────────────────────────────────────────────────────── */
const lHamburger = document.getElementById('lHamburger');
const lMobileMenu = document.getElementById('lMobileMenu');
lHamburger?.addEventListener('click', () => {
  lMobileMenu.classList.toggle('open');
});

/* ── Smooth scroll for anchor links ──────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    const target = document.querySelector(a.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      lMobileMenu?.classList.remove('open');
    }
  });
});

/* ── Particle canvas ──────────────────────────────────────────────────── */
(function initParticles() {
  const canvas = document.getElementById('landing-particles');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let W, H, particles = [];

  function resize() {
    W = canvas.width = window.innerWidth;
    H = canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize, { passive: true });

  const COLORS = ['rgba(124,92,252,', 'rgba(6,214,240,', 'rgba(139,92,246,'];
  for (let i = 0; i < 60; i++) {
    particles.push({
      x: Math.random() * 1920,
      y: Math.random() * 1080,
      r: Math.random() * 1.5 + 0.3,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      alpha: Math.random() * 0.5 + 0.1
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = W; if (p.x > W) p.x = 0;
      if (p.y < 0) p.y = H; if (p.y > H) p.y = 0;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = p.color + p.alpha + ')';
      ctx.fill();
    });
    requestAnimationFrame(draw);
  }
  draw();
})();

/* ── GSAP Hero entrance ───────────────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  if (typeof gsap === 'undefined') return;

  gsap.registerPlugin(ScrollTrigger);

  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
  tl.to('.hero-badge',  { opacity: 1, y: 0, duration: 0.7, delay: 0.2 })
    .to('.hero-title',  { opacity: 1, y: 0, duration: 0.8 }, '-=0.4')
    .to('.hero-sub',    { opacity: 1, y: 0, duration: 0.7 }, '-=0.5')
    .to('.hero-cta',    { opacity: 1, y: 0, duration: 0.6 }, '-=0.4')
    .to('.hero-trust',  { opacity: 1, y: 0, duration: 0.5 }, '-=0.3')
    .to('.hero-visual', { opacity: 1, y: 0, duration: 0.9 }, '-=0.4');

  // Scroll-triggered reveals
  document.querySelectorAll('[data-reveal]').forEach(el => {
    if (el.classList.contains('hero-badge') || el.classList.contains('hero-title') ||
        el.classList.contains('hero-sub') || el.classList.contains('hero-cta') ||
        el.classList.contains('hero-trust') || el.classList.contains('hero-visual')) return;

    ScrollTrigger.create({
      trigger: el,
      start: 'top 85%',
      onEnter: () => el.classList.add('revealed')
    });
  });
});

/* ── Animated counters ────────────────────────────────────────────────── */
function animateCounter(el, target, duration = 1800) {
  let start = 0;
  const step = target / (duration / 16);
  const timer = setInterval(() => {
    start += step;
    if (start >= target) { start = target; clearInterval(timer); }
    el.textContent = Math.floor(start).toLocaleString();
  }, 16);
}

const counterObserver = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      const target = parseInt(el.dataset.count);
      animateCounter(el, target);
      counterObserver.unobserve(el);
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => counterObserver.observe(el));

/* ── Hero mini chart ──────────────────────────────────────────────────── */
window.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('heroChart');
  if (!canvas || typeof Chart === 'undefined') return;

  const labels = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
  const data = [82, 85, 79, 88, 91, 87, 93];

  new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data,
        borderColor: 'rgba(124,92,252,0.8)',
        backgroundColor: 'rgba(124,92,252,0.08)',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: { display: false }
      },
      animation: { duration: 1500, easing: 'easeInOutQuart' }
    }
  });
});