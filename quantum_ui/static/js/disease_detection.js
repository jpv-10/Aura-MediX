/**
 * AURA MEDIX — Disease Detection Frontend
 * FULLY CONNECTED to backend prediction pipeline with database persistence
 */

document.addEventListener('DOMContentLoaded', function() {
  initializeTabs();
  initializePredictionButtons();
});

function initializeTabs() {
  const tabs = document.querySelectorAll('.disease-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      const target = this.dataset.target;
      switchDiseaseForm(target);
    });
  });
}

function switchDiseaseForm(disease) {
  // Hide all forms
  document.querySelectorAll('.disease-form').forEach(form => {
    form.classList.remove('active');
  });
  
  // Show selected form
  const form = document.getElementById(`form-${disease}`);
  if (form) {
    form.classList.add('active');
  }
  
  // Update active tab
  document.querySelectorAll('.disease-tab').forEach(tab => {
    tab.classList.remove('active');
  });
  document.querySelector(`[data-target="${disease}"]`).classList.add('active');
}

function initializePredictionButtons() {
  document.querySelectorAll('.btn-predict').forEach(btn => {
    btn.addEventListener('click', function() {
      const disease = this.dataset.disease;
      performPrediction(disease);
    });
  });
}

async function performPrediction(disease) {
  const form = document.getElementById(`form-${disease}`);
  if (!form) return;

  const inputs = form.querySelectorAll('input[type="number"]');
  const features = [];
  
  inputs.forEach(input => {
    const value = parseFloat(input.value);
    if (isNaN(value)) {
      alert(`Please fill in all fields. Missing: ${input.parentElement.textContent}`);
      throw new Error('Incomplete form');
    }
    features.push(value);
  });

  const resultPanel = document.getElementById('resultPanel');
  const resultIdle = document.getElementById('resultIdle');
  const resultContent = document.getElementById('resultContent');

  // Show loading state
  resultIdle.style.display = 'none';
  resultContent.classList.remove('hidden');
  resultContent.innerHTML = `
    <div style="text-align: center; padding: 40px 20px;">
      <div style="font-size: 24px; margin-bottom: 12px;">⏳</div>
      <p style="color: var(--text-muted);">Running AI prediction...</p>
      <div style="margin-top: 16px; height: 4px; background: var(--border); border-radius: 2px; overflow: hidden;">
        <div style="height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-primary-light)); animation: pulse 1.5s infinite;"></div>
      </div>
    </div>
  `;

  try {
    const response = await fetch('/ai/predict-disease', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        disease: disease,
        features: features
      })
    });

    const result = await response.json();

    if (response.ok && result.disease) {
      displayResults(result);
      
      // Auto-refresh timeline if it exists
      if (typeof loadTimeline === 'function') {
        setTimeout(() => loadTimeline(), 500);
      }
    } else {
      showError(result.error || 'Prediction failed');
    }
  } catch (error) {
    showError(error.message || 'Network error');
  }
}

function displayResults(result) {
  const resultContent = document.getElementById('resultContent');
  
  const category = result.category || result.prediction_result || 'Unknown';
  const riskPercent = result.risk || 0;
  const categoryColor = getCategoryColor(category);
  const categoryEmoji = getCategoryEmoji(category);

  let html = `
    <div style="margin-bottom: 24px;">
      <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
        <div style="font-size: 32px;">${categoryEmoji}</div>
        <div>
          <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em;">Risk Category</div>
          <div style="font-size: 24px; font-weight: 700; color: ${categoryColor};">${category}</div>
        </div>
      </div>

      <div style="background: var(--gradient-card); border: 1px solid var(--border); border-radius: var(--r-md); padding: 20px;">
        <div style="margin-bottom: 16px;">
          <div>
            <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 4px;">Risk Percentage</div>
            <div style="font-size: 28px; font-weight: 700; color: ${categoryColor};">${riskPercent.toFixed(2)}%</div>
          </div>
        </div>

        <div style="background: rgba(255,255,255,0.02); border: 1px solid var(--border); border-radius: var(--r-sm); padding: 12px; font-size: 13px; color: var(--text-secondary); margin-top: 12px;">
          <strong>Disease:</strong> ${result.disease.toUpperCase()}<br>
          <strong>Model:</strong> ${result.model_used || 'ML Model'}
        </div>
      </div>
    </div>

    <div style="border-top: 1px solid var(--border); padding-top: 16px;">
      <div style="font-size: 14px; font-weight: 600; color: var(--text-primary); margin-bottom: 12px;">AI Recommendations:</div>
      <ul style="list-style: none; padding: 0; margin: 0;">
  `;

  if (result.recommendations && Array.isArray(result.recommendations)) {
    result.recommendations.forEach((rec, idx) => {
      html += `<li style="padding: 8px 0; color: var(--text-secondary); font-size: 13px; line-height: 1.6; border-bottom: 1px solid var(--border-hover); padding-bottom: 12px; margin-bottom: 8px;">
        <span style="color: ${categoryColor}; font-weight: 600;">${idx + 1}.</span> ${rec}
      </li>`;
    });
  }

  html += `
      </ul>
    </div>

    <div style="margin-top: 20px; display: flex; gap: 12px;">
      <button class="btn btn-primary" onclick="downloadResultsPDF()" style="flex: 1;">
        <i class="fas fa-download"></i> Download Report
      </button>
      <button class="btn btn-outline" onclick="resetForm()" style="flex: 1;">
        <i class="fas fa-redo"></i> New Analysis
      </button>
    </div>

    <div style="margin-top: 16px; padding: 12px; background: rgba(96,165,250,0.1); border-left: 3px solid #60A5FA; border-radius: 4px; font-size: 12px; color: var(--text-secondary);">
      <strong>Note:</strong> This prediction has been saved to your health timeline and database. Results are persistent.
    </div>
  `;

  document.getElementById('resultContent').innerHTML = html;
}

function showError(message) {
  const resultContent = document.getElementById('resultContent');
  resultContent.innerHTML = `
    <div style="padding: 24px; text-align: center;">
      <div style="font-size: 48px; margin-bottom: 12px;">⚠️</div>
      <div style="font-size: 16px; font-weight: 600; color: #F87171; margin-bottom: 8px;">Prediction Failed</div>
      <p style="color: var(--text-muted); margin-bottom: 16px;">${message}</p>
      <button class="btn btn-outline" onclick="resetForm()">Try Again</button>
    </div>
  `;
}

function getCategoryColor(category) {
  const c = (category || '').toLowerCase();
  if (c.includes('critical')) return '#EF4444';
  if (c.includes('high')) return '#F97316';
  if (c.includes('medium')) return '#FBBF24';
  if (c.includes('low')) return '#34D399';
  return '#A78BFA';
}

function getCategoryEmoji(category) {
  const c = (category || '').toLowerCase();
  if (c.includes('critical')) return '🚨';
  if (c.includes('high')) return '⚠️';
  if (c.includes('medium')) return '📊';
  if (c.includes('low')) return '✅';
  return '🔬';
}

function downloadResultsPDF() {
  window.location.href = '/api/v1/reports/download?report_type=health_summary';
}

function resetForm() {
  document.getElementById('resultContent').classList.add('hidden');
  document.getElementById('resultIdle').style.display = 'block';
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.value = '';
  });
}