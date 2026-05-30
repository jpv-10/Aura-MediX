/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Dashboard JS
   ═══════════════════════════════════════════════════════════════════════ */

/* ── Time greeting ────────────────────────────────────────────────────── */
(function() {
  const h = new Date().getHours();
  const el = document.getElementById('timeGreeting');
  if (!el) return;
  if (h < 12) el.textContent = 'morning';
  else if (h < 17) el.textContent = 'afternoon';
  else el.textContent = 'evening';
})();

/* ── KPI entrance animation ───────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.kpi-card, .feat-card');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(16px)';
    setTimeout(() => {
      card.style.transition = 'opacity .45s ease, transform .45s cubic-bezier(.16,1,.3,1), border-color .25s ease, box-shadow .25s ease';
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, 60 + i * 40);
  });
});

/* ── Live vitals polling ──────────────────────────────────────────────── */
function refreshVitals() {
  fetch('/pulse/realtime/metrics')
    .then(r => r.json())
    .then(data => {
      const hrEl = document.getElementById('heartRateVal');
      const spo2El = document.getElementById('spo2Val');
      const tempEl = document.getElementById('tempVal');
      const bpEl = document.getElementById('bpVal');
      if (hrEl) hrEl.textContent = data.heart_rate || 72;
      if (spo2El) spo2El.textContent = data.oxygen_saturation || 98;
      if (tempEl) tempEl.textContent = data.temperature || '37.0';
      if (bpEl) {
        const bp = data.blood_pressure;
        if (bp) bpEl.textContent = `${bp.systolic}/${bp.diastolic}`;
      }
    })
    .catch(() => {}); // Silently fail — show static values
}
refreshVitals();
setInterval(refreshVitals, 15000);

/* ── Vitals Trend Chart ───────────────────────────────────────────────── */
let vitalsTrendChart = null;

function buildVitalsTrendChart(days = 7) {
  const canvas = document.getElementById('vitalsTrendChart');
  if (!canvas || typeof Chart === 'undefined') return;

  // Generate mock data for demo
  const labels = [];
  const hrData = [], spo2Data = [], tempData = [];
  const now = new Date();
  for (let i = days - 1; i >= 0; i--) {
    const d = new Date(now);
    d.setDate(d.getDate() - i);
    labels.push(d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    hrData.push(65 + Math.floor(Math.random() * 25));
    spo2Data.push(96 + Math.floor(Math.random() * 4));
    tempData.push(+(36.4 + Math.random() * 0.8).toFixed(1));
  }

  if (vitalsTrendChart) vitalsTrendChart.destroy();

  vitalsTrendChart = new Chart(canvas, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Heart Rate (bpm)',
          data: hrData,
          borderColor: 'rgba(124,92,252,0.8)',
          backgroundColor: 'rgba(124,92,252,0.06)',
          borderWidth: 2, pointRadius: 3,
          pointBackgroundColor: 'rgba(124,92,252,0.8)',
          fill: true, tension: 0.4
        },
        {
          label: 'SpO₂ (%)',
          data: spo2Data,
          borderColor: 'rgba(6,214,240,0.8)',
          backgroundColor: 'rgba(6,214,240,0.04)',
          borderWidth: 2, pointRadius: 3,
          pointBackgroundColor: 'rgba(6,214,240,0.8)',
          fill: true, tension: 0.4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          labels: { color: 'rgba(155,163,192,0.8)', font: { size: 11 }, boxWidth: 12 }
        },
        tooltip: {
          backgroundColor: 'rgba(9,13,26,0.95)',
          borderColor: 'rgba(124,92,252,0.3)',
          borderWidth: 1,
          titleColor: '#edf0f7',
          bodyColor: 'rgba(155,163,192,0.9)',
          padding: 10
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { color: 'rgba(155,163,192,0.6)', font: { size: 10 } }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.03)' },
          ticks: { color: 'rgba(155,163,192,0.6)', font: { size: 10 } }
        }
      }
    }
  });
}

/* ── Wellness Radar Chart ─────────────────────────────────────────────── */
function buildWellnessRadar() {
  const canvas = document.getElementById('wellnessRadar');
  if (!canvas || typeof Chart === 'undefined') return;

  new Chart(canvas, {
    type: 'radar',
    data: {
      labels: ['Sleep', 'Stress', 'Mood', 'Activity', 'Nutrition', 'Social'],
      datasets: [{
        label: 'Wellness',
        data: [7, 6, 8, 7, 6, 8],
        borderColor: 'rgba(124,92,252,0.8)',
        backgroundColor: 'rgba(124,92,252,0.1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(124,92,252,0.8)',
        pointRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(9,13,26,0.95)',
          borderColor: 'rgba(124,92,252,0.3)',
          borderWidth: 1,
          titleColor: '#edf0f7',
          bodyColor: 'rgba(155,163,192,0.9)'
        }
      },
      scales: {
        r: {
          min: 0, max: 10,
          grid: { color: 'rgba(255,255,255,0.05)' },
          angleLines: { color: 'rgba(255,255,255,0.05)' },
          pointLabels: { color: 'rgba(155,163,192,0.7)', font: { size: 10 } },
          ticks: { display: false }
        }
      }
    }
  });
}

/* ── Chart period toggle ──────────────────────────────────────────────── */
document.querySelectorAll('.chart-period').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.chart-period').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    buildVitalsTrendChart(parseInt(btn.dataset.period));
  });
});

/* ── Init charts ──────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  buildVitalsTrendChart(7);
  buildWellnessRadar();
});
