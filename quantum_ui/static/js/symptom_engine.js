/* ═══════════════════════════════════════════════════════════════════════
   AURA MEDIX — Symptom Engine JS  (Unified v2)
   Design reference: disease_detection.js
   Renders into: #resultContent  (right panel-card)
   All styles consumed from design-system.css + symptom_engine.html head.
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
    'use strict';

    /* ── Shorthand ────────────────────────────────────────────────────── */
    function $(id) { return document.getElementById(id); }

    /* ── HTML escape ──────────────────────────────────────────────────── */
    function escHtml(s) {
        return String(s)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;')
            .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    /* ── Toast notification ───────────────────────────────────────────── */
    function showToast(msg, type) {
        /* Use platform toast container if available */
        const container = document.getElementById('toast-container');
        if (container) {
            const el = document.createElement('div');
            el.style.cssText = [
                'background:rgba(9,13,26,0.97)',
                'border:1px solid rgba(124,58,237,0.25)',
                'border-radius:10px',
                'padding:12px 16px',
                'font-size:13px',
                'color:#edf0f7',
                'pointer-events:auto',
                'display:flex',
                'align-items:center',
                'gap:8px',
                'max-width:320px',
                'backdrop-filter:blur(12px)'
            ].join(';');
            const icon = type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ';
            el.textContent = icon + ' ' + msg;
            container.appendChild(el);
            setTimeout(() => el.remove(), 3500);
            return;
        }

        /* Fallback standalone toast */
        let t = $('se-toast');
        if (!t) {
            t = document.createElement('div');
            t.id = 'se-toast';
            t.style.cssText = [
                'position:fixed', 'bottom:28px', 'right:28px', 'z-index:9999',
                'background:rgba(13,11,20,.96)', 'border:1px solid rgba(255,255,255,0.08)',
                'border-left:3px solid #7C3AED', 'color:#F0EBF8',
                'padding:14px 20px', 'border-radius:12px', 'font-size:13px',
                'font-weight:500', 'opacity:0', 'transform:translateX(20px)',
                'transition:all .35s ease', 'pointer-events:none',
                'min-width:240px', 'backdrop-filter:blur(20px)'
            ].join(';');
            document.body.appendChild(t);
        }
        const clr = { error:'#F87171', success:'#34D399', warning:'#FBBF24', info:'#7C3AED' };
        t.style.borderLeftColor = clr[type] || clr.info;
        t.textContent = msg;
        t.style.opacity = '1'; t.style.transform = 'translateX(0)';
        clearTimeout(t._timer);
        t._timer = setTimeout(() => {
            t.style.opacity = '0'; t.style.transform = 'translateX(20px)';
        }, 3200);
    }

    /* ── Disease database ─────────────────────────────────────────────── */
    const DISEASE_DB = [
        {
            name: 'Common Cold', icon: '🤧',
            keywords: ['runny nose','sneezing','sore throat','cough','mild fever','congestion','fatigue','cold'],
            baseConf: 76, baseSev: 20,
            recs: [
                'Rest at home for 7–10 days',
                'Stay hydrated with warm fluids & broths',
                'Honey & ginger for throat soothing',
                'Vitamin C and zinc supplementation'
            ]
        },
        {
            name: 'Influenza (Flu)', icon: '🌡️',
            keywords: ['fever','chills','muscle ache','headache','cough','fatigue','body pain','flu'],
            baseConf: 68, baseSev: 55,
            recs: [
                'Seek antivirals (e.g. oseltamivir) within 48 h of onset',
                'Rest and isolate for 24 h after fever resolves',
                'Monitor for complications such as pneumonia',
                'Paracetamol / ibuprofen for fever & pain'
            ]
        },
        {
            name: 'Tension Headache', icon: '🤕',
            keywords: ['headache','tension','neck pain','stress','eye strain','pressure','dull pain'],
            baseConf: 80, baseSev: 30,
            recs: [
                'Apply warm compress to neck & shoulders',
                'Practice progressive muscle relaxation',
                'Stay hydrated; reduce caffeine intake',
                'OTC analgesics if needed; rest in a quiet room'
            ]
        },
        {
            name: 'Allergic Rhinitis', icon: '🌸',
            keywords: ['sneezing','runny nose','itchy eyes','congestion','watery eyes','allergy','hayfever'],
            baseConf: 73, baseSev: 22,
            recs: [
                'Identify and avoid allergen triggers',
                'Daily non-sedating antihistamine',
                'Saline nasal rinse morning & evening',
                'HEPA air purifier in bedroom'
            ]
        },
        {
            name: 'Gastroenteritis', icon: '🤢',
            keywords: ['nausea','vomiting','diarrhoea','stomach ache','cramps','abdominal pain','stomach pain'],
            baseConf: 66, baseSev: 42,
            recs: [
                'Fast 4–6 h to allow stomach to settle',
                'Small sips of ORS / clear fluids frequently',
                'BRAT diet (banana, rice, apple, toast) when tolerating food',
                'Seek care if high fever or blood in stool'
            ]
        },
        {
            name: 'Anxiety / Stress Response', icon: '😰',
            keywords: ['anxious','stressed','panic','palpitations','shortness of breath','dizziness','racing heart','anxiety'],
            baseConf: 70, baseSev: 38,
            recs: [
                '4-7-8 breathing technique for immediate relief',
                'Daily mindfulness or meditation practice (10 min)',
                'Limit caffeine and reduce screen time before bed',
                'Consider speaking with a mental health professional'
            ]
        },
        {
            name: 'Migraine', icon: '💫',
            keywords: ['severe headache','pulsing','nausea','light sensitivity','aura','vomiting','one-sided headache'],
            baseConf: 74, baseSev: 58,
            recs: [
                'Rest immediately in a dark, quiet room',
                'Use prescribed triptans or OTC analgesics early',
                'Apply cold compress to forehead or neck',
                'Keep a migraine diary to identify triggers'
            ]
        },
        {
            name: 'COVID-19 / Viral Infection', icon: '🦠',
            keywords: ['fever','cough','loss of smell','fatigue','shortness of breath','sore throat','body ache','covid'],
            baseConf: 62, baseSev: 62,
            recs: [
                'Isolate immediately and take a rapid antigen test',
                'Rest, hydrate, and take paracetamol for symptoms',
                'Monitor SpO₂ with a pulse oximeter',
                'Seek emergency care if oxygen drops below 94%'
            ]
        },
        {
            name: 'Hypertension', icon: '💓',
            keywords: ['high blood pressure','chest pain','headache','dizziness','blurred vision','hypertension'],
            baseConf: 60, baseSev: 70,
            recs: [
                'Measure blood pressure at home twice daily',
                'Reduce sodium intake to < 2 g/day',
                'Increase aerobic activity; avoid smoking',
                'Consult your GP about medication if readings persist'
            ]
        },
        {
            name: 'Iron Deficiency Anaemia', icon: '🩸',
            keywords: ['fatigue','weakness','pale skin','shortness of breath','brittle nails','cold hands','dizziness','anaemia'],
            baseConf: 65, baseSev: 40,
            recs: [
                'Blood test to confirm serum ferritin / iron levels',
                'Iron-rich foods: red meat, lentils, dark leafy greens',
                'Vitamin C alongside iron meals to boost absorption',
                'Consider iron supplementation under medical guidance'
            ]
        }
    ];

    /* ── Scoring ──────────────────────────────────────────────────────── */
    function scoreDisease(disease, tokens) {
        let hits = 0;
        tokens.forEach(tok => {
            if (disease.keywords.some(kw => kw.includes(tok) || tok.includes(kw.split(' ')[0]))) hits++;
        });
        return hits;
    }

    /* ── Severity helpers ─────────────────────────────────────────────── */
    function getSeverityStyle(s) {
        if (s < 25) return { color: '#34D399', text: 'Mild — monitor at home' };
        if (s < 50) return { color: '#FBBF24', text: 'Moderate — consider a GP visit' };
        if (s < 75) return { color: '#F87171', text: 'Significant — seek medical attention' };
        return             { color: '#EF4444', text: 'Severe — urgent medical attention needed' };
    }

    function getOverallRec(maxSev, stress, anxiety) {
        if (maxSev >= 65 || stress >= 8 || anxiety >= 8) return {
            icon:  '🚨',
            title: 'Urgent Attention Recommended',
            body:  'Your symptoms indicate a potentially serious condition. Please consult a doctor or visit an urgent care clinic promptly. Do not delay seeking professional medical advice.'
        };
        if (maxSev >= 40) return {
            icon:  '🏥',
            title: 'Schedule a Doctor\'s Visit',
            body:  'Your symptoms are moderate and warrant a professional evaluation. Book an appointment with your GP within 24–48 hours and monitor for any worsening symptoms.'
        };
        return {
            icon:  '🌿',
            title: 'Home Care Likely Sufficient',
            body:  'Your symptoms appear mild and manageable at home. Follow the recommendations above, rest well, stay hydrated, and monitor over the next 2–3 days. Consult a doctor if symptoms persist or worsen.'
        };
    }

    /* ── Active symptom tags ──────────────────────────────────────────── */
    const activeTags = new Set();

    function initTags() {
        document.querySelectorAll('.symptom-tag').forEach(tag => {
            tag.addEventListener('click', () => {
                const sym = tag.dataset.sym;
                if (!sym) return;
                if (activeTags.has(sym)) {
                    activeTags.delete(sym);
                    tag.classList.remove('active');
                } else {
                    activeTags.add(sym);
                    tag.classList.add('active');
                }
                mergeTagsIntoInput();
            });
        });
    }

    function mergeTagsIntoInput() {
        const inp = $('symptomInput');
        if (!inp) return;
        const typed = inp.value.split(',').map(s => s.trim()).filter(s => s && !activeTags.has(s));
        inp.value = [...activeTags, ...typed].join(', ');
    }

    /* ── Mood buttons ─────────────────────────────────────────────────── */
    function initMoodButtons() {
        document.querySelectorAll('.mood-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
            });
        });
    }

    /* ── Slider sync ──────────────────────────────────────────────────── */
    function initSliders() {
        const pairs = [
            ['stressSlider',  'stressVal'],
            ['anxietySlider', 'anxietyVal'],
            ['energySlider',  'energyVal'],
            ['sleepSlider',   'sleepVal']
        ];
        pairs.forEach(([sliderId, valId]) => {
            const slider = $(sliderId);
            const valEl  = $(valId);
            if (!slider) return;
            function sync() {
                const pct = (parseFloat(slider.value) / parseFloat(slider.max)) * 100;
                slider.style.setProperty('--val', pct + '%');
                if (valEl) valEl.textContent = slider.value;
            }
            sync();
            slider.addEventListener('input', sync);
        });
    }

    /* ── Main analysis ────────────────────────────────────────────────── */
    function analyzeSymptoms() {
        const inp    = $('symptomInput');
        const rawTxt = inp ? inp.value.trim() : '';
        const allSyms = [
            ...activeTags,
            ...rawTxt.split(',').map(s => s.trim()).filter(Boolean)
        ];

        if (allSyms.length === 0) {
            showToast('Please enter or select at least one symptom.', 'error');
            return;
        }

        const btn = $('analyzeBtn');
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = `
                <span style="display:inline-flex;align-items:center;justify-content:center;gap:10px;">
                    <span style="
                        width:16px;height:16px;
                        border:2.5px solid rgba(255,255,255,0.3);
                        border-top-color:#fff;border-radius:50%;
                        animation:se-spin .8s linear infinite;
                        display:inline-block;"></span>
                    Analyzing…
                </span>`;
        }

        /* Simulate model latency (1.8 s) then render */
        setTimeout(() => {
            const tokens = allSyms.map(s => s.toLowerCase().trim());

            const scored = DISEASE_DB.map(d => {
                const hits = scoreDisease(d, tokens);
                return {
                    ...d,
                    confidence: Math.min(
                        d.baseConf + Math.min(hits * 8, 20) + Math.floor(Math.random() * 8),
                        95
                    ),
                    severity: Math.max(5, d.baseSev + Math.floor(Math.random() * 14) - 7),
                    hits
                };
            }).filter(d => d.hits > 0 || Math.random() > 0.55);

            const top3 = scored.sort((a, b) => b.confidence - a.confidence).slice(0, 3);
            if (top3.length === 0) top3.push({ ...DISEASE_DB[0], confidence: 55, severity: 20 });

            renderResults(allSyms, top3);

            if (btn) {
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-brain"></i>&nbsp; Analyze Symptoms';
            }
            showToast('Analysis complete ✓', 'success');
        }, 1800);
    }

    /* ── Render results ───────────────────────────────────────────────── */
    /* Writes a single rich HTML block into #resultContent (right panel).
       Mirrors disease_detection.js renderPredictionResult() structure.    */
    function renderResults(symptoms, conditions) {
        const idle    = $('resultIdle');
        const content = $('resultContent');
        if (!content) return;
        if (idle) idle.classList.add('hidden');
        content.classList.remove('hidden');

        /* ── Wellness data ── */
        const stress  = parseInt($('stressSlider')?.value  ?? 5);
        const anxiety = parseInt($('anxietySlider')?.value ?? 5);
        const energy  = parseInt($('energySlider')?.value  ?? 5);
        const sleep   = parseInt($('sleepSlider')?.value   ?? 5);
        const moodRaw = document.querySelector('.mood-btn.selected')?.dataset.mood || 'okay';
        const mood    = moodRaw.charAt(0).toUpperCase() + moodRaw.slice(1);

        /* ── Hero numbers from top condition ── */
        const top     = conditions[0];
        const topConf = top ? top.confidence : 0;
        const topSev  = top ? getSeverityStyle(top.severity) : { color: '#A097B8', text: 'Unknown' };
        const topSevLabel = topSev.text.split('—')[0].trim();

        /* ── Wellness tiles ── */
        const tiles = [
            { label:'Stress',   val: stress  + '/10', color: stress  > 7 ? '#F87171' : stress  > 4 ? '#FBBF24' : '#34D399' },
            { label:'Anxiety',  val: anxiety + '/10', color: anxiety > 7 ? '#F87171' : anxiety > 4 ? '#FBBF24' : '#34D399' },
            { label:'Energy',   val: energy  + '/10', color: energy  < 3 ? '#F87171' : energy  < 6 ? '#FBBF24' : '#34D399' },
            { label:'Sleep',    val: sleep   + '/10', color: sleep   < 4 ? '#F87171' : sleep   < 7 ? '#FBBF24' : '#34D399' },
            { label:'Mood',     val: mood,            color: '#A78BFA' },
            { label:'Symptoms', val: symptoms.length + ' noted', color: '#2DD4BF' }
        ];
        const tilesHtml = `
            <div class="se-wellness-grid">
                ${tiles.map((t, i) => `
                    <div class="se-tile" style="--tc:${t.color};animation-delay:${i * 0.05}s">
                        <div class="se-tile-val">${escHtml(t.val)}</div>
                        <div class="se-tile-label">${escHtml(t.label)}</div>
                    </div>`).join('')}
            </div>`;

        /* ── Diagnosis cards ── */
        const cardsHtml = conditions.map((c, idx) => {
            const sc = getSeverityStyle(c.severity);
            const recsHtml = c.recs.map(r => `
                <div class="se-rec-item">
                    <span class="se-rec-bullet">›</span>
                    <span>${escHtml(r)}</span>
                </div>`).join('');

            return `
                <div class="se-diag-card" style="--dc:${sc.color};animation-delay:${(idx * 0.08) + 0.15}s">
                    <div class="se-diag-top">
                        <div class="se-diag-left">
                            <div class="se-diag-icon">${escHtml(c.icon)}</div>
                            <div class="se-diag-name">${escHtml(c.name)}</div>
                        </div>
                        <div class="se-conf-badge">
                            <div class="se-conf-num" style="color:${sc.color}">${c.confidence}%</div>
                            <div class="se-conf-lbl">Confidence</div>
                        </div>
                    </div>

                    <div class="se-sev-row">
                        <span>Severity Level</span><span>${c.severity}%</span>
                    </div>
                    <div class="se-sev-track">
                        <div class="se-sev-fill" id="se-sev-${idx}"
                            style="background:${sc.color};box-shadow:0 0 6px ${sc.color}55"></div>
                    </div>
                    <div style="margin-bottom:14px">
                        <span class="se-sev-tag" style="--dc:${sc.color}">${escHtml(sc.text)}</span>
                    </div>

                    <div class="se-recs-heading">Recommendations</div>
                    ${recsHtml}
                </div>`;
        }).join('');

        /* ── Overall recommendation ── */
        const maxSev  = Math.max(...conditions.map(c => c.severity));
        const overall = getOverallRec(maxSev, stress, anxiety);
        const listedSyms = symptoms.slice(0, 4).map(escHtml).join(', ')
                         + (symptoms.length > 4 ? '…' : '');

        /* ── Compose full result HTML (mirrors disease_detection layout) ── */
        content.innerHTML = `

            <!-- Hero number — mirrors disease_detection's risk % display -->
            <div style="text-align:center;margin-bottom:22px;animation:se-fade-up 0.5s ease-out">
                <div style="
                    font-size:48px;font-weight:700;
                    font-family:var(--f-head);color:#A78BFA;
                    letter-spacing:-0.03em;line-height:1">
                    ${topConf}%
                </div>
                <div style="font-size:13px;color:var(--color-text-muted);margin-top:4px">
                    Top Match Confidence
                </div>
                <div style="
                    display:inline-flex;align-items:center;gap:6px;
                    padding:5px 14px;border-radius:9999px;
                    background:${topSev.color}20;border:1px solid ${topSev.color}40;
                    color:${topSev.color};font-size:12px;font-weight:700;
                    margin-top:10px;text-transform:uppercase;letter-spacing:0.05em">
                    ${escHtml(topSevLabel)}
                </div>
                <div style="font-size:12px;color:var(--color-text-muted);margin-top:8px">
                    Based on ${symptoms.length} symptom${symptoms.length !== 1 ? 's' : ''}:
                    <span style="color:var(--color-text-secondary)">${listedSyms}</span>
                </div>
            </div>

            <!-- Progress bar — mirrors disease_detection risk bar -->
            <div style="margin-bottom:20px">
                <div style="
                    display:flex;justify-content:space-between;
                    font-size:12px;color:var(--color-text-muted);margin-bottom:6px">
                    <span>Overall Confidence</span><span>${topConf}%</span>
                </div>
                <div style="height:6px;background:rgba(255,255,255,0.06);border-radius:3px;overflow:hidden">
                    <div id="se-hero-bar" style="
                        height:100%;width:0%;background:#A78BFA;
                        border-radius:3px;
                        transition:width 1s cubic-bezier(0.34,1.2,0.64,1)"></div>
                </div>
            </div>

            <!-- Disclaimer (matches disease_detection style) -->
            <div style="
                padding:10px 13px;
                background:rgba(248,113,113,0.06);
                border:1px solid rgba(248,113,113,0.18);
                border-radius:var(--r-md);margin-bottom:20px;
                display:flex;gap:10px;align-items:flex-start;
                font-size:11.5px;color:#fca5a5;line-height:1.5">
                <span style="font-size:14px;flex-shrink:0;margin-top:1px">⚠️</span>
                <span>
                    <strong>Medical Disclaimer:</strong> This AI analysis is for informational
                    purposes only and does not constitute medical advice. Always consult a
                    qualified healthcare professional for diagnosis and treatment.
                </span>
            </div>

            <!-- Wellness summary -->
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                letter-spacing:0.08em;color:#A78BFA;margin-bottom:12px">
                Wellness Summary
            </div>
            ${tilesHtml}

            <!-- Possible conditions -->
            <div style="font-size:11px;font-weight:700;text-transform:uppercase;
                letter-spacing:0.08em;color:#A78BFA;margin-bottom:12px">
                Possible Conditions
            </div>
            <div class="se-diag-grid">${cardsHtml}</div>

            <!-- Overall recommendation -->
            <div class="se-overall">
                <span class="se-overall-icon">${overall.icon}</span>
                <div>
                    <div class="se-overall-title">${escHtml(overall.title)}</div>
                    <div class="se-overall-body">${escHtml(overall.body)}</div>
                </div>
            </div>

            <!-- Footer disclaimer (mirrors disease_detection) -->
            <div class="se-disclaimer">
                <i class="fas fa-info-circle" style="color:#8B5CF6"></i>
                <strong style="color:rgba(255,255,255,0.4)"> Disclaimer:</strong>
                This is an AI-assisted estimation only. Always consult a licensed physician
                for clinical evaluation and diagnosis.
            </div>

            <!-- AI Doctor CTA -->
            <a href="/modules/ai-doctor" class="se-ai-btn">
                <i class="fas fa-robot"></i> Discuss with AURA AI
            </a>

            <!-- New analysis -->
            <button class="se-reset-btn" onclick="resetAnalysis()">
                ↺&nbsp; New Analysis
            </button>
        `;

        /* ── Animate hero bar ── */
        requestAnimationFrame(() => requestAnimationFrame(() => {
            const heroBar = $('se-hero-bar');
            if (heroBar) heroBar.style.width = topConf + '%';
        }));

        /* ── Animate per-condition severity bars ── */
        requestAnimationFrame(() => requestAnimationFrame(() => {
            conditions.forEach((c, idx) => {
                const bar = $('se-sev-' + idx);
                if (bar) bar.style.width = c.severity + '%';
            });
        }));

        /* ── Scroll result panel into view ── */
        const panel = $('resultPanel');
        if (panel) panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /* ── Reset ────────────────────────────────────────────────────────── */
    function resetAnalysis() {
        const idle    = $('resultIdle');
        const content = $('resultContent');
        if (idle)    { idle.classList.remove('hidden'); }
        if (content) { content.classList.add('hidden'); content.innerHTML = ''; }

        const inp = $('symptomInput');
        if (inp) inp.value = '';

        activeTags.clear();
        document.querySelectorAll('.symptom-tag').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.mood-btn').forEach(b => b.classList.remove('selected'));

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /* ── Expose to inline onclick handlers ───────────────────────────── */
    window.analyzeSymptoms = analyzeSymptoms;
    window.resetAnalysis   = resetAnalysis;
    window.showToast       = window.showToast || showToast;

    /* ── Init on DOM ready ────────────────────────────────────────────── */
    document.addEventListener('DOMContentLoaded', () => {
        initTags();
        initMoodButtons();
        initSliders();

        /* Ctrl/Cmd+Enter shortcut in textarea */
        const inp = $('symptomInput');
        if (inp) {
            inp.addEventListener('keydown', e => {
                if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) analyzeSymptoms();
            });
        }

        /* Button click (belt-and-suspenders alongside onclick attr) */
        const btn = $('analyzeBtn');
        if (btn) btn.addEventListener('click', analyzeSymptoms);
    });

})();