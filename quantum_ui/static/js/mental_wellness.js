/**
 * MEDI AI NEXUS — Mental Wellness JS v3.0
 */
let selectedMood = 'neutral';

function selectMood(mood, btn) {
  selectedMood = mood;
  document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  updateWellnessPreview();
}

function updateWellnessPreview() {
  const stress     = parseInt(document.getElementById('stressSlider')?.value || 5);
  const anxiety    = parseInt(document.getElementById('anxietySlider')?.value || 5);
  const depression = parseInt(document.getElementById('depressionSlider')?.value || 5);
  const wellness   = Math.max(0, Math.min(100, 100 - ((stress + anxiety + depression) / 3) * 10));
  drawWellnessGauge(wellness);
  const el = document.getElementById('wellnessScorePreview');
  if (el) el.textContent = Math.round(wellness);
}

function drawWellnessGauge(value) {
  const canvas = document.getElementById('wellnessGauge');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const cx = W / 2, cy = H - 8, r = Math.min(W, H * 2) / 2 - 14;
  const color = value >= 75 ? '#6ee7b7' : value >= 50 ? '#fcd34d' : '#fca5a5';
  // Track
  ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, 2 * Math.PI);
  ctx.strokeStyle = 'rgba(255,255,255,0.07)'; ctx.lineWidth = 12; ctx.lineCap = 'round'; ctx.stroke();
  // Fill
  const angle = Math.PI + (value / 100) * Math.PI;
  ctx.beginPath(); ctx.arc(cx, cy, r, Math.PI, angle);
  ctx.strokeStyle = color; ctx.lineWidth = 12;
  ctx.shadowBlur = 14; ctx.shadowColor = color; ctx.stroke();
}

async function assessMentalHealth() {
  const stress     = parseInt(document.getElementById('stressSlider')?.value || 5);
  const anxiety    = parseInt(document.getElementById('anxietySlider')?.value || 5);
  const depression = parseInt(document.getElementById('depressionSlider')?.value || 5);

  const btn = document.querySelector('.btn-predict');
  if (btn) { btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analyzing...'; }

  try {
    const res = await fetch('/ai/mental-health-assess', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ stress_level: stress, anxiety_score: anxiety, depression_score: depression, mood: selectedMood })
    });
    const data = await res.json();
    if (data.success) {
      document.getElementById('wellnessPreview')?.classList.add('hidden');
      document.getElementById('wellnessResults')?.classList.remove('hidden');
      renderWellnessResult(data, stress, anxiety, depression);
    }
  } catch { if (typeof showToast !== 'undefined') showToast('Assessment failed', 'error'); }
  finally { if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fas fa-brain"></i> Run Wellness Assessment'; } }
}

function renderWellnessResult(data, stress, anxiety, depression) {
  const score = data.wellness_index;
  const color = score >= 75 ? '#6ee7b7' : score >= 50 ? '#fcd34d' : '#fca5a5';
  const icons = { low: '✅', moderate: '⚠️', high: '🚨' };

  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  const setStyle = (id, prop, val) => { const el = document.getElementById(id); if (el) el.style[prop] = val; };

  setEl('wellnessIcon', icons[data.risk_level] || '🧠');
  setEl('wellnessScore', score.toFixed(1) + '/100');
  setStyle('wellnessScore', 'color', color);
  setEl('wellnessRiskLabel', `Risk Level: ${data.risk_level.toUpperCase()}`);
  setStyle('wellnessRiskLabel', 'color', color);

  // Bars
  const setBar = (id, val) => { const el = document.getElementById(id); if (el) el.style.width = (val * 10) + '%'; };
  setBar('stressBar', stress);
  setBar('anxietyBar', anxiety);
  setBar('depressionBar', depression);

  const recList = document.getElementById('wellnessRecs');
  if (recList) recList.innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join('');

  if (typeof gsap !== 'undefined') {
    gsap.from('#wellnessResults > *', { opacity: 0, y: 12, stagger: 0.08, duration: 0.4 });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateWellnessPreview();
  // Slider live update
  ['stressSlider', 'anxietySlider', 'depressionSlider'].forEach(id => {
    document.getElementById(id)?.addEventListener('input', updateWellnessPreview);
  });
});
