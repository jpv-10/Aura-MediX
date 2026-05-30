/**
 * MEDI AI NEXUS — Health Analytics JS v4.0
 * All charts: responsive:true, maintainAspectRatio:false
 * Containers must have an explicit height set via CSS (height:Npx)
 */

'use strict';

document.addEventListener('DOMContentLoaded', loadAnalytics);

/* ═══════════════════════════════════════════════
   BOOTSTRAP
═══════════════════════════════════════════════ */
async function loadAnalytics() {
  const days = document.getElementById('timeRange')?.value || 30;

  try {
    const [trendsRes, riskRes, wellnessRes] = await Promise.all([
      fetch(`/analytics/health-trends?days=${days}`),
      fetch('/analytics/risk-matrix'),
      fetch('/analytics/wellness-score')
    ]);
    const [trends, risk, wellness] = await Promise.all([
      trendsRes.json(), riskRes.json(), wellnessRes.json()
    ]);

    if (trends.success)   initVitalsTrend(trends.trends);
    if (risk.success)     initRiskRadar(risk.risk_matrix);
    if (wellness.success) initWellnessBar(wellness.components);

    initHRDist();
    initScoreTrend();
    init3D();
  } catch (e) {
    console.warn('Analytics load error:', e);
  }
}

/* Time-range change hook (called by select in template) */
function refreshAnalytics() { loadAnalytics(); }

/* ═══════════════════════════════════════════════
   SHARED CHART DEFAULTS
═══════════════════════════════════════════════ */
const BASE_OPTS = {
  responsive: true,
  maintainAspectRatio: false, // CRITICAL — respects container height
  animation: { duration: 700, easing: 'easeInOutQuart' },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(10,11,16,.96)',
      borderColor: 'rgba(124,58,237,.3)',
      borderWidth: 1,
      titleColor: '#a78bfa',
      bodyColor: '#e2e8f0',
      padding: 10,
      cornerRadius: 8,
      displayColors: false,
    }
  }
};

const SCALE_X = {
  ticks: { color: '#475569', font: { size: 10, family: 'inherit' }, maxRotation: 0 },
  grid:  { color: 'rgba(255,255,255,.04)', drawBorder: false }
};
const SCALE_Y = {
  ticks: { color: '#475569', font: { size: 10, family: 'inherit' } },
  grid:  { color: 'rgba(255,255,255,.04)', drawBorder: false }
};

/* ═══════════════════════════════════════════════
   VITALS TREND — Plotly multi-line
   Container must have explicit height in HTML/CSS
═══════════════════════════════════════════════ */
function initVitalsTrend(data) {
  const el = document.getElementById('vitalsTrendChart');
  if (!el || typeof Plotly === 'undefined') return;

  const traces = [
    {
      x: data.labels, y: data.heart_rate,
      name: 'Heart Rate', mode: 'lines',
      line: { color: '#a78bfa', width: 2 },
      fill: 'tozeroy', fillcolor: 'rgba(124,58,237,.06)'
    },
    {
      x: data.labels, y: data.oxygen,
      name: 'O₂ Sat', mode: 'lines',
      line: { color: '#67e8f9', width: 2 },
      fill: 'tozeroy', fillcolor: 'rgba(34,211,238,.05)'
    },
    {
      x: data.labels, y: data.bp_sys,
      name: 'BP Sys', mode: 'lines',
      line: { color: '#f9a8d4', width: 2 },
      fill: 'tozeroy', fillcolor: 'rgba(236,72,153,.05)'
    }
  ];

  const layout = {
    paper_bgcolor: 'transparent',
    plot_bgcolor:  'transparent',
    font: { color: '#64748b', family: 'inherit', size: 11 },
    xaxis: {
      gridcolor: 'rgba(255,255,255,.04)',
      linecolor: 'rgba(255,255,255,.06)',
      tickfont: { size: 10 }
    },
    yaxis: {
      gridcolor: 'rgba(255,255,255,.04)',
      linecolor: 'rgba(255,255,255,.06)',
      tickfont: { size: 10 }
    },
    legend: {
      font: { color: '#94a3b8', size: 10 },
      bgcolor: 'transparent',
      orientation: 'h',
      y: -0.15
    },
    margin: { t: 8, r: 8, b: 48, l: 40 },
    hovermode: 'x unified',
    hoverlabel: {
      bgcolor: 'rgba(10,11,16,.96)',
      bordercolor: 'rgba(124,58,237,.3)',
      font: { color: '#e2e8f0', size: 11 }
    }
  };

  Plotly.newPlot(el, traces, layout, {
    responsive: true,
    displayModeBar: false,
    // useResizeHandler keeps Plotly inside the container on window resize
    useResizeHandler: true
  });
}

/* ═══════════════════════════════════════════════
   RISK RADAR — Chart.js radar
═══════════════════════════════════════════════ */
function initRiskRadar(rm) {
  const ctx = document.getElementById('riskRadarChart');
  if (!ctx) return;

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: Object.keys(rm).map(k =>
        k.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
      ),
      datasets: [{
        data: Object.values(rm),
        backgroundColor: 'rgba(239,68,68,.1)',
        borderColor: '#fca5a5',
        pointBackgroundColor: '#fca5a5',
        pointRadius: 4,
        borderWidth: 2
      }]
    },
    options: {
      ...BASE_OPTS,
      scales: {
        r: {
          min: 0, max: 50,
          ticks: { display: false },
          grid:         { color: 'rgba(255,255,255,.06)' },
          angleLines:   { color: 'rgba(255,255,255,.06)' },
          pointLabels:  { color: '#94a3b8', font: { size: 10, family: 'inherit' } }
        }
      }
    }
  });
}

/* ═══════════════════════════════════════════════
   WELLNESS BAR — Chart.js bar
═══════════════════════════════════════════════ */
function initWellnessBar(c) {
  const ctx = document.getElementById('wellnessBarChart');
  if (!ctx) return;

  const labels = Object.keys(c).map(k => k.charAt(0).toUpperCase() + k.slice(1));
  const values = Object.values(c);
  const bg    = values.map(v => v >= 75 ? 'rgba(16,185,129,.5)'  : v >= 50 ? 'rgba(124,58,237,.5)' : 'rgba(239,68,68,.5)');
  const border= values.map(v => v >= 75 ? '#6ee7b7'              : v >= 50 ? '#a78bfa'              : '#fca5a5');

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: bg,
        borderColor: border,
        borderWidth: 1,
        borderRadius: 6
      }]
    },
    options: {
      ...BASE_OPTS,
      scales: {
        x: { ...SCALE_X, grid: { display: false } },
        y: { ...SCALE_Y, max: 100 }
      }
    }
  });
}

/* ═══════════════════════════════════════════════
   HEART-RATE DISTRIBUTION — mini sparkline
═══════════════════════════════════════════════ */
function initHRDist() {
  const ctx = document.getElementById('hrDistChart');
  if (!ctx) return;

  const data = Array.from({ length: 24 }, () => 60 + Math.random() * 40);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels: data.map((_, i) => i),
      datasets: [{
        data,
        borderColor: '#f9a8d4',
        backgroundColor: 'rgba(236,72,153,.08)',
        tension: .4,
        fill: true,
        pointRadius: 0,
        borderWidth: 2
      }]
    },
    options: {
      ...BASE_OPTS,
      plugins: { ...BASE_OPTS.plugins, tooltip: { enabled: false } },
      scales: {
        x: { display: false },
        y: { ...SCALE_Y, beginAtZero: false }
      }
    }
  });
}

/* ═══════════════════════════════════════════════
   HEALTH SCORE TREND — 12-week line
═══════════════════════════════════════════════ */
function initScoreTrend() {
  const ctx = document.getElementById('healthScoreChart');
  if (!ctx) return;

  const labels = Array.from({ length: 12 }, (_, i) => `W${i + 1}`);
  const data   = labels.map((_, i) => 70 + i * 1.5 + Math.random() * 4);

  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        data,
        borderColor: '#fcd34d',
        backgroundColor: 'rgba(245,158,11,.08)',
        tension: .4,
        fill: true,
        pointRadius: 3,
        pointHoverRadius: 5,
        pointBackgroundColor: '#fcd34d',
        pointBorderColor: 'transparent',
        borderWidth: 2
      }]
    },
    options: {
      ...BASE_OPTS,
      scales: {
        x: { ...SCALE_X, grid: { display: false } },
        y: { ...SCALE_Y, min: 60, max: 100 }
      }
    }
  });
}

/* ═══════════════════════════════════════════════
   3-D SCATTER — Plotly
   Container must have height set in CSS/HTML
═══════════════════════════════════════════════ */
function init3D() {
  const el = document.getElementById('plotly3dChart');
  if (!el || typeof Plotly === 'undefined') return;

  const n = 60;
  const x = Array.from({ length: n }, () => Math.random() * 100);
  const y = Array.from({ length: n }, () => Math.random() * 100);
  const z = x.map((xi, i) => xi * 0.3 + y[i] * 0.4 + Math.random() * 20);

  Plotly.newPlot(el, [{
    type: 'scatter3d',
    mode: 'markers',
    x, y, z,
    marker: {
      size: 5,
      color: z,
      colorscale: [[0, '#7c3aed'], [0.5, '#ec4899'], [1, '#22d3ee']],
      opacity: .85,
      line: { width: 0 }
    }
  }], {
    paper_bgcolor: 'transparent',
    scene: {
      bgcolor: 'transparent',
      xaxis: { title: 'Heart Rate', color: '#64748b', gridcolor: 'rgba(255,255,255,.06)' },
      yaxis: { title: 'O₂ Sat',     color: '#64748b', gridcolor: 'rgba(255,255,255,.06)' },
      zaxis: { title: 'Score',      color: '#64748b', gridcolor: 'rgba(255,255,255,.06)' }
    },
    margin: { t: 0, r: 0, b: 0, l: 0 }
  }, {
    responsive: true,
    displayModeBar: false,
    useResizeHandler: true
  });
}