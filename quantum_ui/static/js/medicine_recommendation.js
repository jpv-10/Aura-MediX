/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Medicine Recommendation JS
   Design reference: disease_detection.js (premium unified platform)
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    /* ── Helpers ──────────────────────────────────────────────────────── */
    function escHtml(s) {
        return String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function showToast(msg, type) {
        // Use platform-wide toast if available
        if (window._auraToast) { window._auraToast(msg, type); return; }
        const container = document.getElementById('toast-container');
        if (container) {
            const el = document.createElement('div');
            el.style.cssText = [
                'background:rgba(13,11,20,0.97)',
                'border:1px solid rgba(124,58,237,0.25)',
                'border-radius:10px',
                'padding:12px 16px',
                'font-size:13px',
                'color:#F0EBF8',
                'pointer-events:auto',
                'display:flex',
                'align-items:center',
                'gap:8px',
                'max-width:320px',
                'backdrop-filter:blur(12px)'
            ].join(';');
            const icons = { error: '⚠', success: '✓', warning: '⚡', info: 'ℹ' };
            const colors = { error: '#F87171', success: '#34D399', warning: '#FBBF24', info: '#A78BFA' };
            el.style.borderLeft = `3px solid ${colors[type] || colors.info}`;
            el.textContent = (icons[type] || 'ℹ') + ' ' + msg;
            container.appendChild(el);
            setTimeout(() => el.remove(), 3500);
            return;
        }
        // Fallback inline toast
        let t = document.getElementById('mr-toast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'mr-toast';
            t.style.cssText = [
                'position:fixed', 'bottom:28px', 'right:28px', 'z-index:9999',
                'background:rgba(13,11,20,.96)',
                'border:1px solid rgba(255,255,255,0.08)',
                'border-left:3px solid #7C3AED',
                'color:#F0EBF8', 'padding:14px 20px',
                'border-radius:12px', 'font-size:13px', 'font-weight:500',
                'opacity:0', 'transform:translateX(20px)',
                'transition:all .35s ease',
                'pointer-events:none', 'min-width:240px',
                'backdrop-filter:blur(20px)',
                'box-shadow:0 8px 32px rgba(0,0,0,0.4)'
            ].join(';');
            document.body.appendChild(t);
        }
        const colors = { error: '#F87171', success: '#34D399', warning: '#FBBF24', info: '#7C3AED' };
        t.style.borderLeftColor = colors[type] || colors.info;
        t.textContent = msg;
        t.style.opacity = '1';
        t.style.transform = 'translateX(0)';
        clearTimeout(t._timer);
        t._timer = setTimeout(() => {
            t.style.opacity = '0';
            t.style.transform = 'translateX(20px)';
        }, 3200);
    }

    /* ── Medicine database ────────────────────────────────────────────── */
    const MEDICINE_DB = {
        'headache': [
            { name: 'Paracetamol', type: 'Analgesic', icon: '💊', rating: 4.8,
              dosage: 'Take 500 mg every 4–6 hours (max 4,000 mg/day)',
              sideEffects: ['Liver sensitivity (high doses)', 'Allergic reactions (rare)'],
              precautions: ['Do not exceed 4,000 mg per day', 'Avoid with other acetaminophen products', 'Monitor liver function if used chronically'],
              warning: 'Do not combine with alcohol or other pain relievers' },
            { name: 'Ibuprofen', type: 'NSAID Anti-inflammatory', icon: '💊', rating: 4.7,
              dosage: 'Take 200–400 mg every 4–6 hours',
              sideEffects: ['Stomach upset', 'Dizziness', 'Heartburn'],
              precautions: ['Take with food or milk', 'Not for long-term daily use', 'Caution with ulcer or kidney conditions'],
              warning: 'May increase heart attack or stroke risk with prolonged use' }
        ],
        'fever': [
            { name: 'Paracetamol', type: 'Antipyretic', icon: '💊', rating: 4.8,
              dosage: 'Take 500–650 mg every 4 hours (max 4 doses/day)',
              sideEffects: ['Rare allergic reactions', 'Liver sensitivity'],
              precautions: ['Stay well hydrated', 'Monitor temperature every 2 hours', 'Do not exceed 4 doses in 24 hours'],
              warning: 'Seek medical attention if fever persists over 3 days' },
            { name: 'Ibuprofen', type: 'Fever Reducer', icon: '💊', rating: 4.6,
              dosage: 'Take 200–400 mg every 6–8 hours',
              sideEffects: ['Stomach upset', 'Dizziness'],
              precautions: ['Take with food', 'Do not exceed 1,200 mg daily without a doctor', 'Monitor body temperature throughout'],
              warning: 'Not suitable for children under 6 months' }
        ],
        'cough': [
            { name: 'Dextromethorphan', type: 'Cough Suppressant', icon: '💊', rating: 4.5,
              dosage: 'Take 10–20 mg every 4–6 hours (max 120 mg/day)',
              sideEffects: ['Drowsiness', 'Dizziness', 'Constipation'],
              precautions: ['Do not use if taking MAOIs', 'Avoid driving — may cause drowsiness', 'Maximum 120 mg daily'],
              warning: 'Do not use for productive coughs — may trap mucus' },
            { name: 'Guaifenesin', type: 'Expectorant', icon: '💊', rating: 4.4,
              dosage: 'Take 200–400 mg every 4 hours',
              sideEffects: ['Nausea', 'Vomiting (rare)'],
              precautions: ['Drink plenty of fluids', 'Safe during pregnancy', 'Take with warm fluids for best effect'],
              warning: 'Best suited for productive coughs with mucus' }
        ],
        'sore throat': [
            { name: 'Ibuprofen', type: 'Pain Reliever', icon: '💊', rating: 4.7,
              dosage: 'Take 200–400 mg every 6–8 hours',
              sideEffects: ['Stomach upset', 'Heartburn'],
              precautions: ['Take with food', 'Stay hydrated with warm fluids', 'Avoid hot beverages immediately after dose'],
              warning: 'Consult a doctor if symptoms persist over 1 week' },
            { name: 'Throat Lozenges', type: 'Soothing Agent', icon: '🍬', rating: 4.3,
              dosage: 'Dissolve 1 lozenge in mouth every 2–3 hours',
              sideEffects: ['Mouth numbness (temporary)', 'Mild taste changes'],
              precautions: ['Do not swallow whole', 'Keep away from children under 4', 'May cause temporary taste changes'],
              warning: 'Not a substitute for antibiotics if bacterial infection is suspected' }
        ],
        'cold': [
            { name: 'Vitamin C', type: 'Immune Support', icon: '🍊', rating: 4.2,
              dosage: 'Take 500–1,000 mg daily',
              sideEffects: ['Mild stomach upset', 'Diarrhea at high doses'],
              precautions: ['Take with food for better absorption', 'Start at lower doses', 'Flush with plenty of fluids'],
              warning: 'May cause kidney stones in susceptible individuals' },
            { name: 'Zinc Lozenges', type: 'Duration Reducer', icon: '⚡', rating: 4.1,
              dosage: 'Take 15–30 mg within 24 hours of symptom onset',
              sideEffects: ['Metallic taste', 'Nausea'],
              precautions: ['Use within the first day of symptoms', 'Do not exceed 40 mg daily', 'May interfere with certain medications'],
              warning: 'Prolonged use may cause copper deficiency' }
        ],
        'nausea': [
            { name: 'Metoclopramide', type: 'Anti-nausea', icon: '💊', rating: 4.6,
              dosage: 'Take 10 mg three times daily, 30 min before meals',
              sideEffects: ['Drowsiness', 'Dizziness', 'Restlessness'],
              precautions: ['Do not operate machinery', 'Monitor for involuntary movements'],
              warning: 'Long-term use may cause tardive dyskinesia' },
            { name: 'Ginger', type: 'Natural Remedy', icon: '🌿', rating: 4.3,
              dosage: '500–1,000 mg or ginger tea up to 4 times daily',
              sideEffects: ['Heartburn', 'Mouth irritation (rare)'],
              precautions: ['Safe for most people', 'Caution with anticoagulants — may thin blood', 'Take with food if stomach-sensitive'],
              warning: 'Not recommended before surgery due to blood-thinning effects' }
        ],
        'insomnia': [
            { name: 'Melatonin', type: 'Sleep Aid', icon: '😴', rating: 4.4,
              dosage: 'Take 2–10 mg 30 minutes before bedtime',
              sideEffects: ['Morning grogginess', 'Headache', 'Vivid dreams'],
              precautions: ['Not habit-forming when used correctly', 'Use for short-term only', 'Avoid driving next morning if groggy'],
              warning: 'Do not use long-term without medical supervision' },
            { name: 'Diphenhydramine', type: 'Sleep Inducer', icon: '💊', rating: 4.2,
              dosage: 'Take 25–50 mg before bedtime',
              sideEffects: ['Morning drowsiness', 'Dry mouth', 'Dizziness'],
              precautions: ['Avoid alcohol', 'Do not drive or operate machinery', 'May cause dependency with regular use'],
              warning: 'Do not use long-term without medical supervision' }
        ],
        'allergies': [
            { name: 'Cetirizine', type: 'Antihistamine', icon: '💊', rating: 4.7,
              dosage: 'Take 5–10 mg once daily',
              sideEffects: ['Mild drowsiness', 'Dry mouth'],
              precautions: ['May cause drowsiness — avoid driving', 'Identify and avoid allergen triggers', 'Can be taken with or without food'],
              warning: 'Do not exceed 20 mg daily' },
            { name: 'Loratadine', type: 'Non-drowsy Antihistamine', icon: '💊', rating: 4.8,
              dosage: 'Take 10 mg once daily',
              sideEffects: ['Headache (rare)', 'Dry mouth (rare)'],
              precautions: ['Minimal drowsiness — safe for daytime use', 'Take at the same time daily', 'Safe for long-term seasonal use'],
              warning: 'Avoid grapefruit juice — may increase drug levels' }
        ],
        'stomach pain': [
            { name: 'Omeprazole', type: 'Proton Pump Inhibitor', icon: '💊', rating: 4.6,
              dosage: 'Take 20 mg once daily, 30 min before first meal',
              sideEffects: ['Headache', 'Nausea', 'Diarrhea'],
              precautions: ['Long-term use affects B12 absorption', 'Regular check-ups recommended', 'Do not crush or chew capsule'],
              warning: 'Prolonged use increases fracture risk — regular monitoring advised' },
            { name: 'Antacid (Calcium Carbonate)', type: 'Acid Neutralizer', icon: '💊', rating: 4.3,
              dosage: 'Take 1–2 tablets as needed, up to 4 times daily',
              sideEffects: ['Constipation', 'Bloating'],
              precautions: ['May interfere with absorption of other medications', 'Take 2 hours apart from other drugs', 'Monitor calcium intake if using frequently'],
              warning: 'May cause milk-alkali syndrome with excess use over time' }
        ]
    };

    /* ── Search logic ─────────────────────────────────────────────────── */
    function searchMedicines(queryRaw) {
        const query = queryRaw.trim().toLowerCase();
        if (!query) {
            showToast('Please enter at least one symptom.', 'warning');
            return;
        }

        const resultsContainer = document.getElementById('resultsContainer');
        if (!resultsContainer) return;

        // Loading state — mirrors disease_detection loading spinner
        resultsContainer.innerHTML = `
            <div class="mr-loading">
                <div class="mr-spinner"></div>
                <div class="mr-loading-text">Searching medicine database…</div>
            </div>`;

        setTimeout(() => {
            let medicines = [];
            for (const [symptom, list] of Object.entries(MEDICINE_DB)) {
                if (query.includes(symptom)) medicines = medicines.concat(list);
            }
            // Deduplicate by name
            medicines = Array.from(new Map(medicines.map(m => [m.name, m])).values());

            if (medicines.length === 0) {
                resultsContainer.innerHTML = `
                    <div class="mr-no-results">
                        <div class="mr-no-results-icon">🔍</div>
                        <div class="mr-no-results-title">No matches found</div>
                        <div class="mr-no-results-hint">
                            Try searching for common symptoms:<br>
                            headache, fever, cough, sore throat, cold,<br>
                            nausea, insomnia, allergies, or stomach pain
                        </div>
                    </div>`;
                return;
            }

            const html = medicines.map((med, idx) => buildMedicineCard(med, idx)).join('');
            resultsContainer.innerHTML = `
                <div class="mr-grid">${html}</div>
                <div class="mr-disclaimer">
                    <i class="fas fa-info-circle" style="color:#8B5CF6"></i>
                    <strong style="color:rgba(255,255,255,0.4)"> Disclaimer:</strong>
                    These recommendations are for informational purposes only and do not replace professional medical advice. Always consult a qualified physician or pharmacist before starting any medication.
                </div>`;

            // Stagger animation delay — mirrors disease_detection reveal
            requestAnimationFrame(() => requestAnimationFrame(() => {
                resultsContainer.querySelectorAll('.mr-card').forEach((card, i) => {
                    card.style.animationDelay = (i * 0.08) + 's';
                });
            }));

            showToast(medicines.length + ' medicine' + (medicines.length > 1 ? 's' : '') + ' found ✓', 'success');
        }, 1100);
    }

    /* ── Build medicine card HTML ─────────────────────────────────────── */
    function buildMedicineCard(med, idx) {
        const sideEffectTags = med.sideEffects
            .map(e => `<span class="mr-tag">${escHtml(e)}</span>`)
            .join('');

        const precautionItems = med.precautions
            .map(p => `
                <div class="mr-precaution">
                    <span class="mr-precaution-bullet">›</span>
                    <span>${escHtml(p)}</span>
                </div>`).join('');

        return `
        <div class="mr-card" style="animation-delay:${idx * 0.08}s">

            <div class="mr-card-head">
                <div class="mr-card-icon">${escHtml(med.icon)}</div>
                <div class="mr-card-name-wrap">
                    <div class="mr-card-name">${escHtml(med.name)}</div>
                    <div class="mr-card-type">${escHtml(med.type)}</div>
                </div>
                <div class="mr-rating">⭐ ${escHtml(String(med.rating))}</div>
            </div>

            <div class="mr-section-lbl">
                <i class="fas fa-prescription-bottle-alt" style="font-size:9px"></i>
                Recommended Dosage
            </div>
            <div class="mr-dosage">${escHtml(med.dosage)}</div>

            <div class="mr-section-lbl">
                <i class="fas fa-exclamation-triangle" style="font-size:9px"></i>
                Possible Side Effects
            </div>
            <div class="mr-tags">${sideEffectTags}</div>

            <div class="mr-warning">
                <span class="mr-warning-icon">⚡</span>
                <span class="mr-warning-text">${escHtml(med.warning)}</span>
            </div>

            <div class="mr-section-lbl">
                <i class="fas fa-shield-alt" style="font-size:9px"></i>
                Important Precautions
            </div>
            ${precautionItems}

            <div class="mr-card-actions">
                <button class="mr-btn mr-btn-primary"
                    onclick="(function(btn){btn.innerHTML='<i class=\\'fas fa-check\\'></i> Saved';btn.style.background='linear-gradient(135deg,#34D399,#059669)';btn.style.boxShadow='0 4px 14px rgba(52,211,153,0.3)'})(this)">
                    <i class="fas fa-bookmark"></i> Save Medicine
                </button>
                <button class="mr-btn mr-btn-outline"
                    onclick="window.showToast && window.showToast('${escHtml(med.name)} added to cart ✓','success')">
                    <i class="fas fa-cart-plus"></i> Add to Cart
                </button>
            </div>
        </div>`;
    }

    /* ── Symptom chip interaction ─────────────────────────────────────── */
    function bindChips() {
        const symptomInput = document.getElementById('symptomInput');
        document.querySelectorAll('.mr-chip').forEach(chip => {
            chip.addEventListener('click', function () {
                const sym = this.dataset.sym;
                if (!sym || !symptomInput) return;

                // Toggle active state
                document.querySelectorAll('.mr-chip').forEach(c => c.classList.remove('active'));
                this.classList.add('active');

                symptomInput.value = sym;
                searchMedicines(sym);
            });
        });
    }

    /* ── Bind search button & input ───────────────────────────────────── */
    function bindUI() {
        const searchBtn    = document.getElementById('searchBtn');
        const symptomInput = document.getElementById('symptomInput');

        if (searchBtn && symptomInput) {
            searchBtn.addEventListener('click', () => {
                // Clear chip active states when manually searching
                document.querySelectorAll('.mr-chip').forEach(c => c.classList.remove('active'));
                searchMedicines(symptomInput.value);
            });

            symptomInput.addEventListener('keydown', e => {
                if (e.key === 'Enter') {
                    document.querySelectorAll('.mr-chip').forEach(c => c.classList.remove('active'));
                    searchMedicines(symptomInput.value);
                }
            });

            // Deactivate chips when user types manually
            symptomInput.addEventListener('input', () => {
                document.querySelectorAll('.mr-chip').forEach(c => c.classList.remove('active'));
            });
        }
    }

    /* ── Expose globals ───────────────────────────────────────────────── */
    window.searchMedicines = searchMedicines;
    window.showToast = window.showToast || showToast;

    /* ── Init ─────────────────────────────────────────────────────────── */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => { bindUI(); bindChips(); });
    } else {
        bindUI();
        bindChips();
    }

})();