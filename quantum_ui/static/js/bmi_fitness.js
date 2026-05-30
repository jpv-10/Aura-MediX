/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — BMI & Fitness JS  (Fixed & Unified v2)
   Design reference: disease_detection.js / design-system.css
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    /* ── Helpers ──────────────────────────────────────────────────────── */
    function $(id)    { return document.getElementById(id); }
    function qAll(s)  { return document.querySelectorAll(s); }

    function escHtml(s) {
        return String(s)
            .replace(/&/g,'&amp;').replace(/</g,'&lt;')
            .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    /* ── Toast (mirrors disease_detection showToastSafe pattern) ─────── */
    function showToast(msg, type) {
        /* Prefer dashboard-level container if present */
        const container = $('toast-container');
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
            const icons = { error: '⚠', success: '✓', warning: '⚠', info: 'ℹ' };
            el.textContent = (icons[type] || 'ℹ') + ' ' + msg;
            container.appendChild(el);
            setTimeout(() => el.remove(), 3500);
            return;
        }

        /* Standalone fallback toast */
        let t = $('bmi-toast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'bmi-toast';
            t.style.cssText = [
                'position:fixed','bottom:28px','right:28px','z-index:9999',
                'background:rgba(13,11,20,0.97)',
                'border:1px solid rgba(255,255,255,0.08)',
                'border-left:3px solid #7C3AED',
                'color:#F0EBF8','padding:14px 20px',
                'border-radius:12px','font-size:13px','font-weight:500',
                'opacity:0','transform:translateX(20px)',
                'transition:all .35s ease','pointer-events:none',
                'min-width:240px','backdrop-filter:blur(20px)'
            ].join(';');
            document.body.appendChild(t);
        }
        const colors = { error:'#F87171', success:'#34D399', warning:'#FBBF24', info:'#7C3AED' };
        t.style.borderLeftColor = colors[type] || colors.info;
        t.textContent = msg;
        t.style.opacity = '1';
        t.style.transform = 'translateX(0)';
        clearTimeout(t._timer);
        t._timer = setTimeout(() => {
            t.style.opacity  = '0';
            t.style.transform = 'translateX(20px)';
        }, 3200);
    }

    /* ── Inject shared CSS (once) ─────────────────────────────────────── */
    function injectStyles() {
        if ($('bmi-unified-styles')) return;
        const s = document.createElement('style');
        s.id = 'bmi-unified-styles';
        s.textContent = `
        /* ── Keyframes ── */
        @keyframes bmi-spin {
            to { transform: rotate(360deg); }
        }
        @keyframes bmi-fade-up {
            from { opacity:0; transform:translateY(12px); }
            to   { opacity:1; transform:translateY(0); }
        }

        /* ── Results grid ── */
        .bmi-results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
            gap: 14px;
            margin-top: 20px;
        }
        @media (max-width: 600px) {
            .bmi-results-grid { grid-template-columns: 1fr; }
            .bmi-rc.full      { grid-column: 1; }
        }

        /* ── Result card — mirrors disease_detection panel-card ── */
        .bmi-rc {
            background: linear-gradient(145deg,rgba(30,26,46,0.9),rgba(26,22,39,0.6));
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 18px;
            position: relative;
            overflow: hidden;
            transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
            animation: bmi-fade-up 0.45s ease both;
        }
        .bmi-rc::before {
            content: '';
            position: absolute; top: 0; left: 0; right: 0; height: 1px;
            background: linear-gradient(90deg,
                transparent,
                var(--bmi-rc-color, rgba(124,58,237,0.5)) 40%,
                transparent);
        }
        .bmi-rc:hover {
            border-color: rgba(255,255,255,0.12);
            transform: translateY(-4px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.4),
                        0 0 32px rgba(124,58,237,0.10);
        }
        .bmi-rc.full { grid-column: 1 / -1; }

        /* ── Card head ── */
        .bmi-rc-head {
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 14px; padding-bottom: 12px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }
        .bmi-rc-icon {
            width: 34px; height: 34px; border-radius: 10px; font-size: 15px;
            background: rgba(255,255,255,0.04);
            border: 1px solid rgba(255,255,255,0.08);
            display: flex; align-items: center; justify-content: center;
            flex-shrink: 0;
        }
        .bmi-rc-title {
            font-size: 13px; font-weight: 700;
            color: rgba(255,255,255,0.85); letter-spacing: 0.01em;
        }

        /* ── Metric row ── */
        .bmi-metric {
            display: flex; justify-content: space-between; align-items: baseline;
            padding: 8px 10px;
            background: rgba(255,255,255,0.02); border-radius: 9px;
            margin: 5px 0; transition: background 0.2s;
        }
        .bmi-metric:hover { background: rgba(124,58,237,0.07); }
        .bmi-metric-lbl { font-size: 12px; color: rgba(255,255,255,0.38); font-weight: 500; }
        .bmi-metric-val { font-size: 14px; font-weight: 600; color: rgba(255,255,255,0.85); }
        .bmi-metric-unit { font-size: 10px; color: rgba(255,255,255,0.28); margin-left:3px; }

        /* ── Rec item (mirrors disease_detection › rows) ── */
        .bmi-rec {
            display: flex; align-items: flex-start; gap: 8px;
            padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
            font-size: 12.5px; color: rgba(255,255,255,0.55); line-height: 1.5;
        }
        .bmi-rec:last-of-type { border-bottom: none; }
        .bmi-rec-bullet { color: #A78BFA; font-weight: 700; flex-shrink: 0; margin-top:1px; }

        /* ── Meal row ── */
        .bmi-meal {
            display: flex; flex-direction: column; gap: 2px;
            padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
        }
        .bmi-meal:last-child { border-bottom: none; }
        .bmi-meal-name {
            font-size: 10px; font-weight: 700; letter-spacing: 0.07em;
            text-transform: uppercase; color: rgba(255,255,255,0.32);
        }
        .bmi-meal-desc { font-size: 12.5px; color: rgba(255,255,255,0.58); }
        .bmi-meal-kcal { font-size: 10.5px; color: rgba(255,255,255,0.25); }

        /* ── Action button (mirrors disease_detection "Discuss" btn) ── */
        .bmi-action-btn {
            width: 100%; margin-top: 14px; padding: 10px 0;
            background: rgba(124,58,237,0.10);
            border: 1px solid rgba(124,58,237,0.25);
            border-radius: 10px; color: #A78BFA;
            font-size: 12.5px; font-weight: 600;
            cursor: pointer; letter-spacing: 0.02em;
            transition: background 0.2s, border-color 0.2s, transform 0.2s, box-shadow 0.2s;
        }
        .bmi-action-btn:hover {
            background: linear-gradient(135deg,#7C3AED,#9333EA);
            border-color: transparent; color: #fff;
            transform: translateY(-2px); box-shadow: 0 8px 24px rgba(124,58,237,0.35);
        }
        .bmi-action-btn:active { transform: translateY(0); }
        `;
        document.head.appendChild(s);
    }

    /* ── BMI Calculation ──────────────────────────────────────────────── */
    function calculateBMI() {
        let h    = parseFloat($('heightInput')?.value);
        let w    = parseFloat($('weightInput')?.value);
        const age      = parseInt($('ageInput')?.value)        || 28;
        const sex      = $('sexInput')?.value                  || 'male';
        const activity = parseFloat($('activityInput')?.value) || 1.55;
        const hUnit    = $('heightUnit')?.value                || 'cm';
        const wUnit    = $('weightUnit')?.value                || 'kg';

        /* Validate */
        if (!h || !w || h <= 0 || w <= 0 || isNaN(h) || isNaN(w)) {
            showToast('Please enter a valid height and weight.', 'error');
            return;
        }

        /* Unit conversion → cm / kg */
        if (hUnit === 'ft') h = h * 30.48;
        if (wUnit === 'lbs') w = w * 0.453592;

        const hM  = h / 100;
        const bmi = parseFloat((w / (hM * hM)).toFixed(1));

        /* Category & colour (mirrors disease_detection risk colours) */
        let cat, color;
        if      (bmi < 18.5) { cat = 'Underweight';   color = '#60A5FA'; }
        else if (bmi < 25)   { cat = 'Healthy Weight'; color = '#34D399'; }
        else if (bmi < 30)   { cat = 'Overweight';     color = '#FBBF24'; }
        else                 { cat = 'Obese';           color = '#F87171'; }

        /* Mifflin–St Jeor BMR → TDEE */
        const bmr = sex === 'male'
            ? 10 * w + 6.25 * h - 5 * age + 5
            : 10 * w + 6.25 * h - 5 * age - 161;
        const tdee = Math.round(bmr * activity);

        /* Ideal weight range (BMI 18.5–24.9) */
        const idealMin = Math.round(18.5 * hM * hM);
        const idealMax = Math.round(24.9 * hM * hM);

        /* Gauge position: BMI 10–45 mapped to 0–100% */
        const gaugePos = Math.min(Math.max(((bmi - 10) / 35) * 100, 2), 98);

        /* ── Update DOM ── */
        injectStyles();

        /* BMI number */
        const numEl = $('bmiDisplay');
        if (numEl) {
            numEl.textContent = bmi.toFixed(1);
            numEl.style.color = color;
        }

        /* Category pill */
        const pill = $('categoryPill');
        if (pill) {
            pill.textContent = cat;
            pill.style.cssText = [
                'display:inline-flex','align-items:center','gap:6px',
                'padding:5px 14px','border-radius:20px',
                'font-weight:700','font-size:11px',
                'text-transform:uppercase','letter-spacing:0.06em',
                `background:${color}20`,
                `border:1px solid ${color}40`,
                `color:${color}`
            ].join(';');
            pill.style.display = 'inline-flex';
        }

        /* Animate gauge marker */
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const marker = $('gaugeMarker');
                if (marker) marker.style.left = gaugePos + '%';
            });
        });

        /* Result cards */
        const cards = $('bmiResultCards');
        if (cards) cards.innerHTML = buildResultCards(bmi, cat, tdee, idealMin, idealMax, w, color);

        /* Reveal result content (mirrors disease_detection hidden → visible) */
        const idle    = $('bmiResultIdle');
        const content = $('bmiResultContent');
        if (idle)    idle.classList.add('hidden');
        if (content) content.classList.remove('hidden');

        showToast(`BMI calculated — ${cat} (${bmi})`, 'success');

        /* Scroll result panel into view */
        const panel = $('bmiResultPanel');
        if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    /* ── Build result cards HTML ──────────────────────────────────────── */
    function buildResultCards(bmi, cat, tdee, idealMin, idealMax, weight, color) {
        const recs    = getRecommendations(cat);
        const meals   = buildMealRows(tdee);
        const diff    = getWeightDiff(weight, idealMin, idealMax);
        const protein = Math.round(weight * 1.6);

        return `
        <div class="bmi-results-grid">

            <!-- BMI Breakdown -->
            <div class="bmi-rc" style="--bmi-rc-color:${color};animation-delay:0s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">📊</div>
                    <div class="bmi-rc-title">BMI Breakdown</div>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Your BMI</span>
                    <span class="bmi-metric-val" style="color:${color};font-size:22px;font-weight:700">${escHtml(String(bmi))}</span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Category</span>
                    <span class="bmi-metric-val" style="color:${color}">${escHtml(cat)}</span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Ideal Range</span>
                    <span class="bmi-metric-val">${idealMin}–${idealMax}<span class="bmi-metric-unit">kg</span></span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">To Ideal</span>
                    <span class="bmi-metric-val" style="font-size:11.5px;color:rgba(255,255,255,0.7)">${escHtml(diff)}</span>
                </div>
            </div>

            <!-- Calorie Targets -->
            <div class="bmi-rc" style="--bmi-rc-color:#FBBF24;animation-delay:0.07s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">🔥</div>
                    <div class="bmi-rc-title">Calorie Targets</div>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Maintenance</span>
                    <span class="bmi-metric-val">${tdee}<span class="bmi-metric-unit">kcal</span></span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Weight Loss (−500)</span>
                    <span class="bmi-metric-val" style="color:#F87171">${tdee - 500}<span class="bmi-metric-unit">kcal</span></span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Weight Gain (+300)</span>
                    <span class="bmi-metric-val" style="color:#34D399">${tdee + 300}<span class="bmi-metric-unit">kcal</span></span>
                </div>
                <div class="bmi-metric">
                    <span class="bmi-metric-lbl">Daily Protein</span>
                    <span class="bmi-metric-val">${protein}<span class="bmi-metric-unit">g/day</span></span>
                </div>
            </div>

            <!-- Hydration -->
            <div class="bmi-rc" style="--bmi-rc-color:#60A5FA;animation-delay:0.10s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">💧</div>
                    <div class="bmi-rc-title">Hydration Target</div>
                </div>
                ${buildHydrationCard(weight, tdee)}
            </div>

            <!-- Workout Plan -->
            <div class="bmi-rc" style="--bmi-rc-color:#60A5FA;animation-delay:0.14s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">🏃</div>
                    <div class="bmi-rc-title">Workout Plan</div>
                </div>
                ${recs.workout.map(r => `
                    <div class="bmi-rec">
                        <span class="bmi-rec-bullet">›</span>
                        <span>${escHtml(r)}</span>
                    </div>`).join('')}
                <button class="bmi-action-btn" onclick="window.showToast('Workout plan saved ✓','success')">Save Workout Plan</button>
            </div>

            <!-- Nutrition Advice -->
            <div class="bmi-rc" style="--bmi-rc-color:#34D399;animation-delay:0.21s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">🥗</div>
                    <div class="bmi-rc-title">Nutrition Advice</div>
                </div>
                ${recs.nutrition.map(r => `
                    <div class="bmi-rec">
                        <span class="bmi-rec-bullet">›</span>
                        <span>${escHtml(r)}</span>
                    </div>`).join('')}
                <button class="bmi-action-btn" onclick="window.showToast('Meal plan loading…','info')">View Meal Plan</button>
            </div>

            <!-- Sample Meal Plan (full-width) -->
            <div class="bmi-rc full" style="--bmi-rc-color:#A78BFA;animation-delay:0.28s">
                <div class="bmi-rc-head">
                    <div class="bmi-rc-icon">🍽️</div>
                    <div class="bmi-rc-title">Sample Meal Plan</div>
                </div>
                ${meals}
                <button class="bmi-action-btn" onclick="window.showToast('Generating your 7-day meal plan…','info')">Generate 7-Day Plan</button>
            </div>

        </div>

        <div style="margin-top:16px;padding:10px 14px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);border-radius:10px;font-size:12px;color:rgba(255,255,255,0.3);line-height:1.5">
            <i class="fas fa-info-circle" style="color:#8B5CF6"></i>
            <strong style="color:rgba(255,255,255,0.4)">Disclaimer:</strong>
            BMI is a screening tool only. For a personalised health plan consult a qualified healthcare professional.
        </div>

        <a href="/modules/ai-doctor" class="btn btn-primary" style="width:100%;justify-content:center;margin-top:14px;display:flex;align-items:center;gap:8px">
            <i class="fas fa-robot"></i> Discuss with AURA AI
        </a>`;
    }

    /* ── Hydration card rows ──────────────────────────────────────────── */
    function buildHydrationCard(weight, tdee) {
        /* 35 ml/kg body weight, rounded to nearest 100 ml */
        const daily = Math.round((weight * 35) / 100) * 100;
        const glasses = Math.round(daily / 250);
        return `
        <div class="bmi-metric">
            <span class="bmi-metric-lbl">Daily Water</span>
            <span class="bmi-metric-val">${(daily / 1000).toFixed(1)}<span class="bmi-metric-unit">L / day</span></span>
        </div>
        <div class="bmi-metric">
            <span class="bmi-metric-lbl">In Glasses</span>
            <span class="bmi-metric-val">${glasses}<span class="bmi-metric-unit">× 250 ml</span></span>
        </div>
        <div class="bmi-metric">
            <span class="bmi-metric-lbl">Extra for exercise</span>
            <span class="bmi-metric-val">+500<span class="bmi-metric-unit">ml</span></span>
        </div>
        <div class="bmi-metric">
            <span class="bmi-metric-lbl">First glass</span>
            <span class="bmi-metric-val" style="font-size:11px;color:rgba(255,255,255,0.6)">Immediately on waking</span>
        </div>`;
    }

    /* ── Weight diff string ───────────────────────────────────────────── */
    function getWeightDiff(w, min, max) {
        if (w < min) return '+' + (min - w).toFixed(1) + ' kg to gain';
        if (w > max) return '−' + (w - max).toFixed(1) + ' kg to lose';
        return '✓ Already in ideal range';
    }

    /* ── Recommendations by category ─────────────────────────────────── */
    function getRecommendations(cat) {
        const map = {
            'Underweight': {
                workout:   [
                    'Strength training 3–4×/week (compound lifts)',
                    'Progressive overload each session',
                    'Limit excessive cardio',
                    'Rest 48 h between muscle groups'
                ],
                nutrition: [
                    'Caloric surplus +300–500 kcal/day',
                    'Protein 1.6–2.0 g/kg bodyweight',
                    'Eat every 3–4 h; don\'t skip meals',
                    'Include healthy fats (avocado, nuts, olive oil)'
                ]
            },
            'Healthy Weight': {
                workout:   [
                    '30 min moderate cardio, 3–5×/week',
                    'Strength training 2–3×/week',
                    'Daily mobility & stretching (10 min)',
                    'Aim for 8,000–10,000 steps/day'
                ],
                nutrition: [
                    'Balanced diet at maintenance calories',
                    'Prioritise whole foods & vegetables',
                    'Limit ultra-processed foods',
                    'Hydrate well — 2–3 L water/day'
                ]
            },
            'Overweight': {
                workout:   [
                    'Cardio 45–60 min, 5×/week',
                    'HIIT 2–3×/week for calorie burn',
                    'Strength training 2×/week to preserve muscle',
                    'Daily walks: 10,000+ steps'
                ],
                nutrition: [
                    'Caloric deficit of 500 kcal/day',
                    'Reduce refined carbs & added sugars',
                    'Increase fibre (vegetables, legumes, oats)',
                    'Control portions; eat slowly'
                ]
            },
            'Obese': {
                workout:   [
                    'Low-impact cardio (swimming, cycling) daily',
                    'Walk 20–30 min after each main meal',
                    'Resistance bands for gentle strength work',
                    'Consult a physiotherapist before high-impact exercise'
                ],
                nutrition: [
                    'Structured plan — consider a registered dietitian',
                    'Eliminate sugary beverages entirely',
                    'Prioritise protein & fibre at every meal',
                    'Track food intake for accountability'
                ]
            }
        };
        return map[cat] || map['Healthy Weight'];
    }

    /* ── Meal plan rows ───────────────────────────────────────────────── */
    function buildMealRows(tdee) {
        const meals = [
            { meal: 'Breakfast', desc: 'Oats, Greek yoghurt & mixed berries',        kcal: Math.round(tdee * 0.25) },
            { meal: 'Lunch',     desc: 'Grilled chicken, brown rice & steamed veg',  kcal: Math.round(tdee * 0.35) },
            { meal: 'Snack',     desc: 'Almonds & a piece of fruit',                 kcal: Math.round(tdee * 0.10) },
            { meal: 'Dinner',    desc: 'Salmon, sweet potato & mixed greens',        kcal: Math.round(tdee * 0.30) }
        ];
        return meals.map(m => `
            <div class="bmi-meal">
                <span class="bmi-meal-name">${escHtml(m.meal)}</span>
                <span class="bmi-meal-desc">${escHtml(m.desc)}</span>
                <span class="bmi-meal-kcal">~${m.kcal} kcal</span>
            </div>`).join('');
    }

    /* ── Log water (idle card action) ────────────────────────────────── */
    function logWater() {
        const bar   = $('hydrationBar');
        const label = $('hydrationPct');
        if (!bar) { showToast('Hydration tracker not found', 'info'); return; }

        let cur = parseInt(label ? label.textContent : '75') || 75;
        if (cur < 100) {
            cur = Math.min(cur + 12, 100);
            bar.style.width = cur + '%';
            if (label) label.textContent = cur + '%';
            showToast('Water logged! Keep it up 💧', 'success');
        } else {
            showToast('Daily water goal already reached! 🎉', 'success');
        }
    }

    /* ── Calculate button loading state ──────────────────────────────── */
    function setCalcBtnLoading(loading) {
        const btn = $('calculateBtn');
        if (!btn) return;
        if (loading) {
            btn.disabled = true;
            btn.innerHTML = `<span style="display:inline-block;width:14px;height:14px;border:2px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:bmi-spin 0.7s linear infinite;vertical-align:middle;margin-right:6px"></span> Calculating…`;
        } else {
            btn.disabled   = false;
            btn.innerHTML  = '<i class="fas fa-calculator"></i> Calculate BMI';
        }
    }

    /* ── Public calculate entry point ────────────────────────────────── */
    function calculateBMIWithLoader() {
        injectStyles();
        setCalcBtnLoading(true);
        setTimeout(() => {
            try {
                calculateBMI();
            } catch (e) {
                showToast('Calculation error — check your inputs.', 'error');
                console.error('[BMI Fitness]', e);
            } finally {
                setCalcBtnLoading(false);
            }
        }, 100);
    }

    /* ── Expose globals ───────────────────────────────────────────────── */
    window.calculateBMI = calculateBMIWithLoader;
    window.logWater     = logWater;
    window.showToast    = showToast;

    /* ── Init ─────────────────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', () => {
        injectStyles();

        /* Bind calculate button */
        const btn = $('calculateBtn');
        if (btn) btn.addEventListener('click', calculateBMIWithLoader);

        /* Enter key on any input field triggers calculation */
        qAll('#heightInput, #weightInput, #ageInput').forEach(inp => {
            inp.addEventListener('keydown', e => {
                if (e.key === 'Enter') calculateBMIWithLoader();
            });
        });
    });

})();