/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Core JS Utilities v6.0 PREMIUM
   Toast · Clock · Ripple · Scroll animations · Sidebar toggle
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Toast notifications — premium glassmorphism style ───────────────── */
window.showToast = function(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = `
      position:fixed;bottom:1.5rem;right:1.5rem;z-index:9999;
      display:flex;flex-direction:column;gap:8px;pointer-events:none;
    `;
    document.body.appendChild(container);
  }

  const icons = {
    success: 'check-circle',
    error:   'exclamation-circle',
    info:    'info-circle',
    warning: 'exclamation-triangle'
  };
  const borderColors = {
    success: 'rgba(52,211,153,0.30)',
    error:   'rgba(248,113,113,0.30)',
    info:    'rgba(124,58,237,0.30)',
    warning: 'rgba(251,191,36,0.30)'
  };
  const glows = {
    success: '0 0 24px rgba(52,211,153,0.10)',
    error:   '0 0 24px rgba(248,113,113,0.10)',
    info:    '0 0 24px rgba(124,58,237,0.14)',
    warning: '0 0 24px rgba(251,191,36,0.10)'
  };
  const iconColors = {
    success: '#34D399',
    error:   '#F87171',
    info:    '#A78BFA',
    warning: '#FBBF24'
  };

  const toast = document.createElement('div');
  toast.style.cssText = `
    display:flex;align-items:center;gap:10px;
    padding:12px 16px;
    background:rgba(10,8,18,0.92);
    backdrop-filter:blur(20px) saturate(160%);
    -webkit-backdrop-filter:blur(20px) saturate(160%);
    border:1px solid ${borderColors[type] || borderColors.info};
    border-radius:14px;
    font-size:13px;font-weight:500;
    box-shadow:${glows[type] || glows.info},0 8px 40px rgba(0,0,0,0.50);
    pointer-events:auto;
    transform:translateX(calc(100% + 24px));
    transition:transform 0.38s cubic-bezier(0.16,1,0.3,1),opacity 0.38s ease;
    max-width:320px;min-width:220px;
    opacity:0;
  `;
  toast.innerHTML = `
    <i class="fas fa-${icons[type] || icons.info}" style="flex-shrink:0;color:${iconColors[type] || iconColors.info};font-size:14px"></i>
    <span style="color:#E0D9F0;line-height:1.4">${message}</span>
  `;
  container.appendChild(toast);

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      toast.style.transform = 'translateX(0)';
      toast.style.opacity   = '1';
    });
  });

  setTimeout(() => {
    toast.style.transform = 'translateX(calc(100% + 24px))';
    toast.style.opacity   = '0';
    setTimeout(() => toast.remove(), 420);
  }, duration);
};

/* ── Live clock ───────────────────────────────────────────────────────── */
function updateClock() {
  const el = document.getElementById('liveTime');
  if (!el) return;
  el.textContent = new Date().toLocaleTimeString('en-US', {
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
}
updateClock();
setInterval(updateClock, 1000);

/* ── Ripple effect on .btn elements ──────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('.btn');
  if (!btn) return;
  const rect   = btn.getBoundingClientRect();
  const size   = Math.max(rect.width, rect.height) * 1.2;
  const ripple = document.createElement('span');
  ripple.style.cssText = `
    position:absolute;border-radius:50%;
    width:${size}px;height:${size}px;
    left:${e.clientX - rect.left - size / 2}px;
    top:${e.clientY - rect.top  - size / 2}px;
    background:rgba(255,255,255,0.12);
    transform:scale(0);
    animation:ripple-anim 0.55s ease-out forwards;
    pointer-events:none;
  `;
  if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
});

/* Inject ripple keyframe once */
if (!document.getElementById('ripple-style')) {
  const s = document.createElement('style');
  s.id = 'ripple-style';
  s.textContent = '@keyframes ripple-anim{to{transform:scale(2.5);opacity:0}}';
  document.head.appendChild(s);
}

/* ── Auto-dismiss flash alerts ────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      alert.style.opacity    = '0';
      alert.style.transform  = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 420);
    }, 4200);
  });
});

/* ── Animate-on-scroll observer ──────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const targets = document.querySelectorAll('.animate-on-scroll');
  if (!targets.length) return;

  const io = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

  targets.forEach(el => io.observe(el));
});

/* ── Sidebar toggle ───────────────────────────────────────────────────── */
let _sideCollapsed = false;

function toggleSide() {
  const nav  = document.getElementById('sideNav');
  const wrap = document.getElementById('mainWrap');
  const topN = document.getElementById('topNav');
  const icon = document.getElementById('sideToggleIcon');

  if (!nav) return;
  _sideCollapsed = !_sideCollapsed;

  nav.classList.toggle('collapsed', _sideCollapsed);
  if (wrap) wrap.classList.toggle('expanded', _sideCollapsed);
  if (topN) topN.classList.toggle('expanded', _sideCollapsed);
  if (icon) {
    icon.className = _sideCollapsed
      ? 'fas fa-chevron-right'
      : 'fas fa-chevron-left';
  }
}
window.toggleSide = toggleSide;

/* ── Profile dropdown ─────────────────────────────────────────────────── */
function toggleDrop() {
  const menu = document.getElementById('pMenu');
  const btn  = document.getElementById('profileBtn');
  if (!menu) return;
  const open = menu.classList.toggle('open');
  if (btn) btn.setAttribute('aria-expanded', String(open));
}
window.toggleDrop = toggleDrop;

/* Close dropdown on outside click */
document.addEventListener('click', e => {
  const drop = document.querySelector('.p-drop');
  if (drop && !drop.contains(e.target)) {
    const menu = document.getElementById('pMenu');
    const btn  = document.getElementById('profileBtn');
    if (menu) menu.classList.remove('open');
    if (btn)  btn.setAttribute('aria-expanded', 'false');
  }
});

/* ── Notification panel ───────────────────────────────────────────────── */
function openNotif() {
  const panel = document.getElementById('notifPanel');
  if (panel) { panel.classList.add('open'); panel.setAttribute('aria-hidden','false'); }
}
function closeNotif() {
  const panel = document.getElementById('notifPanel');
  if (panel) { panel.classList.remove('open'); panel.setAttribute('aria-hidden','true'); }
}
window.openNotif  = openNotif;
window.closeNotif = closeNotif;

document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('notifBtn');
  if (btn) btn.addEventListener('click', openNotif);
});

/* ── Keyboard shortcuts ───────────────────────────────────────────────── */
document.addEventListener('keydown', e => {
  // '/' focuses global search
  if (e.key === '/' && !['INPUT','TEXTAREA'].includes(document.activeElement.tagName)) {
    e.preventDefault();
    const search = document.getElementById('globalSearch');
    if (search) search.focus();
  }
  // Escape closes dropdown / notification panel
  if (e.key === 'Escape') {
    const menu = document.getElementById('pMenu');
    if (menu) menu.classList.remove('open');
    closeNotif();
  }
});