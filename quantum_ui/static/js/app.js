/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Global App JS v5.0
   Toast · Ripple · Sidebar · Clock · IntersectionObserver
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Toast notifications ──────────────────────────────────────────────── */
window.showToast = function(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.style.cssText = 'position:fixed;bottom:24px;right:24px;z-index:9999;display:flex;flex-direction:column;gap:8px;pointer-events:none;';
    document.body.appendChild(container);
  }
  const icons   = { success:'check-circle', error:'exclamation-circle', info:'info-circle', warning:'exclamation-triangle' };
  const borders = { success:'rgba(16,185,129,0.3)', error:'rgba(239,68,68,0.3)', info:'rgba(124,58,237,0.3)', warning:'rgba(245,158,11,0.3)' };
  const colors  = { success:'#34D399', error:'#FB7185', info:'#A78BFA', warning:'#FCD34D' };
  const toast = document.createElement('div');
  toast.style.cssText = `display:flex;align-items:center;gap:10px;padding:12px 16px;background:rgba(13,11,20,0.96);backdrop-filter:blur(16px);border:1px solid ${borders[type]||borders.info};border-radius:12px;font-size:13px;font-weight:500;color:${colors[type]||colors.info};box-shadow:0 8px 32px rgba(0,0,0,0.4);pointer-events:auto;transform:translateX(120%);transition:transform 0.3s cubic-bezier(0.16,1,0.3,1);max-width:320px;`;
  toast.innerHTML = `<i class="fas fa-${icons[type]||icons.info}" style="flex-shrink:0"></i><span style="color:#F0EBF8">${message}</span>`;
  container.appendChild(toast);
  requestAnimationFrame(() => requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; }));
  setTimeout(() => { toast.style.transform = 'translateX(120%)'; setTimeout(() => toast.remove(), 350); }, duration);
};

/* ── Ripple on buttons ────────────────────────────────────────────────── */
document.addEventListener('click', e => {
  const btn = e.target.closest('.btn');
  if (!btn) return;
  const rect = btn.getBoundingClientRect();
  const ripple = document.createElement('span');
  const size = Math.max(rect.width, rect.height);
  ripple.style.cssText = `position:absolute;border-radius:50%;width:${size}px;height:${size}px;left:${e.clientX-rect.left-size/2}px;top:${e.clientY-rect.top-size/2}px;background:rgba(255,255,255,0.12);transform:scale(0);animation:ripple-anim 0.5s ease-out forwards;pointer-events:none;`;
  if (getComputedStyle(btn).position === 'static') btn.style.position = 'relative';
  btn.style.overflow = 'hidden';
  btn.appendChild(ripple);
  setTimeout(() => ripple.remove(), 600);
});
if (!document.getElementById('ripple-style')) {
  const s = document.createElement('style');
  s.id = 'ripple-style';
  s.textContent = '@keyframes ripple-anim{to{transform:scale(2.5);opacity:0}}';
  document.head.appendChild(s);
}

/* ── Live clock ───────────────────────────────────────────────────────── */
function updateClock() {
  const el = document.getElementById('liveTime');
  if (!el) return;
  el.textContent = new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
}
updateClock();
setInterval(updateClock, 1000);

/* ── Auto-dismiss flash alerts ────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      alert.style.opacity = '0'; alert.style.transform = 'translateY(-8px)';
      setTimeout(() => alert.remove(), 400);
    }, 4000);
  });
});

/* ── IntersectionObserver for scroll animations ───────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        setTimeout(() => entry.target.classList.add('is-visible'), i * 80);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
});

/* ── Number counter animation ─────────────────────────────────────────── */
window.animateCounter = function(el, target, duration = 800) {
  const start = 0; const startTime = performance.now();
  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    el.textContent = Math.round(start + (target - start) * eased);
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
};

/* ── Sidebar toggle ───────────────────────────────────────────────────── */
let sideOpen = true;
window.toggleSide = function() {
  sideOpen = !sideOpen;
  const side   = document.getElementById('sideNav');
  const main   = document.getElementById('mainWrap');
  const topNav = document.getElementById('topNav');
  const icon   = document.getElementById('sideToggleIcon');
  const isMobile = window.innerWidth <= 768;
  if (isMobile) {
    side.classList.toggle('mobile-open', sideOpen);
  } else {
    if (sideOpen) {
      side.classList.remove('collapsed'); main.classList.remove('expanded'); topNav.classList.remove('expanded');
      icon?.classList.replace('fa-chevron-right','fa-chevron-left');
    } else {
      side.classList.add('collapsed'); main.classList.add('expanded'); topNav.classList.add('expanded');
      icon?.classList.replace('fa-chevron-left','fa-chevron-right');
    }
  }
  sessionStorage.setItem('nexus_sidebar', sideOpen ? 'open' : 'collapsed');
};

/* ── Profile dropdown ─────────────────────────────────────────────────── */
window.toggleDrop = function() {
  const menu = document.getElementById('pMenu');
  const btn  = document.getElementById('profileBtn');
  const open = menu.classList.toggle('open');
  btn.setAttribute('aria-expanded', open);
};

/* ── Notification panel ───────────────────────────────────────────────── */
window.closeNotif = function() {
  const panel = document.getElementById('notifPanel');
  panel.classList.remove('open'); panel.setAttribute('aria-hidden','true');
};

document.addEventListener('DOMContentLoaded', () => {
  /* Notification toggle */
  document.getElementById('notifBtn')?.addEventListener('click', e => {
    e.stopPropagation();
    const panel = document.getElementById('notifPanel');
    const isOpen = panel.classList.toggle('open');
    panel.setAttribute('aria-hidden', !isOpen);
    document.getElementById('pMenu')?.classList.remove('open');
  });

  /* Close on outside click */
  document.addEventListener('click', e => {
    if (!e.target.closest('.p-drop')) {
      document.getElementById('pMenu')?.classList.remove('open');
      document.getElementById('profileBtn')?.setAttribute('aria-expanded','false');
    }
    if (!e.target.closest('#notifBtn') && !e.target.closest('#notifPanel')) {
      const panel = document.getElementById('notifPanel');
      if (panel?.classList.contains('open')) { panel.classList.remove('open'); panel.setAttribute('aria-hidden','true'); }
    }
  });

  /* Keyboard shortcuts */
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault(); document.getElementById('globalSearch')?.focus();
    }
    if (e.key === 'Escape') { document.getElementById('pMenu')?.classList.remove('open'); closeNotif(); }
  });

  /* Restore sidebar state */
  const pref = sessionStorage.getItem('nexus_sidebar');
  if (pref === 'collapsed') { sideOpen = true; toggleSide(); }
});
