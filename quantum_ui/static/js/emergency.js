/**
 * MEDI AI NEXUS — Emergency Detection JS v4.0
 * Futuristic Critical-Response Module
 */

'use strict';

/* ── State ─────────────────────────────────────────────────────────────── */
let userLocation = null;
let _sirenTimer   = null;

/* ── Severity helpers ───────────────────────────────────────────────────── */
const SEVERITY_CONFIG = {
  CRITICAL: { color: '#fca5a5', track: '#ef4444', pct: 100 },
  HIGH:     { color: '#fcd34d', track: '#f59e0b', pct: 75  },
  MODERATE: { color: '#67e8f9', track: '#22d3ee', pct: 50  },
  LOW:      { color: '#6ee7b7', track: '#10b981', pct: 25  },
};

/* ── Utility ────────────────────────────────────────────────────────────── */
function el(id)       { return document.getElementById(id); }
function show(id)     { el(id)?.classList.remove('hidden'); }
function hide(id)     { el(id)?.classList.add('hidden'); }
function setText(id, v){ const e = el(id); if (e) e.textContent = v; }

/* ── Public API ─────────────────────────────────────────────────────────── */

/** Fill textarea and immediately analyse */
function quickEmergency(symptoms) {
  const input = el('emergencyInput');
  if (input) input.value = symptoms;
  analyzeEmergency();
}

/** Request geolocation and display coordinates */
function getLocation() {
  if (!navigator.geolocation) return;

  navigator.geolocation.getCurrentPosition(
    pos => {
      userLocation = { lat: pos.coords.latitude, lng: pos.coords.longitude };
      const status = el('locationStatus');
      if (status) {
        status.textContent = `📍 ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}`;
        status.style.color = '#6ee7b7';
      }
    },
    () => {
      const status = el('locationStatus');
      if (status) status.textContent = 'Location unavailable';
    }
  );
}

/** Main analysis function — calls backend /emergency/detect */
async function analyzeEmergency() {
  const symptoms = el('emergencyInput')?.value.trim();
  if (!symptoms) return;

  _setAnalyzing(true);
  _clearResults();

  try {
    const payload = { symptoms };
    if (userLocation) { payload.lat = userLocation.lat; payload.lng = userLocation.lng; }

    const res = await fetch('/emergency/detect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.success) {
      renderEmergencyResult(data.result);
    } else {
      _showError('Analysis failed. Please try again.');
    }
  } catch (err) {
    console.error('[Emergency]', err);
    _showError('Connection error. Please try again or call 112 directly.');
  } finally {
    _setAnalyzing(false);
  }
}

/* ── Rendering ──────────────────────────────────────────────────────────── */

function renderEmergencyResult(result) {
  if (result.is_emergency) showCriticalAlert(result);
  else showSafeResult(result);
}

function showCriticalAlert(result) {
  show('criticalAlert');

  const panel = el('emergencyResultPanel');
  if (panel) panel.classList.add('active-alert');

  const cfg   = SEVERITY_CONFIG[result.severity] || SEVERITY_CONFIG.CRITICAL;
  const label = result.severity === 'CRITICAL'
    ? '🚨 CRITICAL EMERGENCY DETECTED'
    : '⚠️ EMERGENCY DETECTED';

  setText('criticalTitle', label);
  setText('criticalTypes',
    'Type: ' + result.detected_types.map(t => t.toUpperCase()).join(', '));

  // Severity value + track
  const sevEl = el('severityValue');
  if (sevEl) { sevEl.textContent = result.severity; sevEl.style.color = cfg.color; }

  const fill = el('severityFill');
  if (fill) {
    fill.style.background = `linear-gradient(90deg, ${cfg.track}99, ${cfg.track})`;
    // Animate fill after a brief paint delay
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { fill.style.width = cfg.pct + '%'; });
    });
  }

  // Immediate actions
  const list = el('actionsList');
  if (list) {
    list.innerHTML = result.immediate_actions
      .map((a, i) => `<li style="animation-delay:${i * 0.06}s">${_escHtml(a)}</li>`)
      .join('');
  }

  // Subtle border siren (non-flashing — colour shift only)
  _clearSiren();
  let tick = 0;
  _sirenTimer = setInterval(() => {
    if (!panel) { _clearSiren(); return; }
    panel.style.borderColor = tick % 2 === 0
      ? 'rgba(239,68,68,0.55)'
      : 'rgba(245,158,11,0.45)';
    if (++tick > 8) _clearSiren();
  }, 400);
}

function showSafeResult(result) {
  show('safeResult');

  setText('safeDesc',
    `No critical emergency symptoms detected. Severity score: ${result.severity_score}/10`);

  const recs = el('safeRecs');
  if (recs) {
    recs.innerHTML = '<ul>' +
      result.immediate_actions.map(a => `<li>${_escHtml(a)}</li>`).join('') +
      '</ul>';
  }
}

/* ── Internal helpers ───────────────────────────────────────────────────── */

function _setAnalyzing(on) {
  const btn = el('analyzeBtn');
  if (!btn) return;
  if (on) {
    btn.innerHTML = '<span class="spinner"></span> ANALYZING…';
    btn.disabled  = true;
  } else {
    btn.innerHTML = '<i class="fas fa-bolt"></i> ANALYZE EMERGENCY';
    btn.disabled  = false;
  }
}

function _clearResults() {
  hide('emergencyIdle');
  hide('criticalAlert');
  hide('safeResult');

  const panel = el('emergencyResultPanel');
  if (panel) {
    panel.classList.remove('active-alert');
    panel.style.borderColor = '';
    panel.style.boxShadow   = '';
  }

  const fill = el('severityFill');
  if (fill) fill.style.width = '0%';

  _clearSiren();
}

function _showError(msg) {
  show('emergencyIdle');
  if (typeof showToast !== 'undefined') showToast(msg, 'error');
}

function _clearSiren() {
  if (_sirenTimer) { clearInterval(_sirenTimer); _sirenTimer = null; }
}

function _escHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}