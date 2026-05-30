# MEDI AI NEXUS v2.1.0
## The Future of Healthcare Intelligence

> A production-grade AI healthcare SaaS platform — dark futuristic UI, real-time ECG monitoring, ML disease prediction, AI doctor chatbot, emergency detection, and 16 intelligent modules.

---

## 🚀 Quick Start (3 steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch
```bash
python run.py
```

### 3. Open Browser
```
http://localhost:5000
```

### Demo Credentials
| Field | Value |
|-------|-------|
| Email | `demo@mediainexus.ai` |
| Password | `Demo@2024` |
| Guest | Click **"Continue as Guest"** on landing page |

---

## 🏗️ Complete Architecture

```
HealthAI/
├── run.py                              # Quick launch script
├── app.py                              # App factory entry
├── wsgi.py                             # Production WSGI entry
├── requirements.txt                    # All dependencies
├── .env                                # Environment config
│
├── nexus_core/                         # ── Core Layer ──
│   ├── __init__.py                     # App factory + extensions
│   ├── quantum_models.py               # SQLAlchemy models (8 tables)
│   ├── config.py                       # Dev/Prod/Test configs
│   └── error_handlers.py              # Custom 404/500/403 pages
│
├── nexus_modules/                      # ── Blueprint Layer ──
│   ├── medix_portal.py                 # Auth + all page routes (17 routes)
│   ├── ai_engine.py                    # AI prediction API endpoints
│   ├── pulse_engine.py                 # Real-time vitals + WebSocket
│   ├── hologram_system.py              # Chat + reports + hospitals
│   ├── neural_analytics.py             # Health analytics API
│   ├── emergency_core.py               # Emergency detection system
│   └── nexus_api.py                    # REST API v1
│
├── ai_engine/                          # ── AI/ML Layer ──
│   ├── nexus_predictor.py              # Disease prediction (RF + GBM)
│   ├── symptom_parser.py               # NLP symptom triage engine
│   ├── nexus_chatbot.py                # AI Doctor knowledge base
│   ├── medicine_engine.py              # Pharmaceutical guidance
│   ├── report_generator.py             # ReportLab PDF generation
│   ├── train_models.py                 # Model training pipeline
│   └── saved_models/                   # Persisted .pkl models
│       ├── diabetes_model.pkl          # 90.0% accuracy
│       ├── heart_model.pkl             # 89.5% accuracy
│       └── hypertension_model.pkl      # 91.0% accuracy
│
├── datasets/                           # ── Sample Data ──
│   ├── diabetes.csv                    # 1000 records
│   ├── heart_disease.csv               # 1000 records
│   ├── hypertension.csv                # 1000 records
│   ├── mental_health.csv               # 800 records
│   ├── vitals_timeseries.csv           # 900 records (10 patients × 90 days)
│   ├── symptom_disease.csv             # 500 records
│   └── generate_datasets.py            # Dataset generator script
│
└── quantum_ui/                         # ── Frontend Layer ──
    ├── templates/
    │   ├── base.html                   # Base (particles + GSAP + CDNs)
    │   ├── dashboard_base.html         # Sidebar + navbar layout
    │   ├── landing.html                # Fullscreen hero + 7 sections
    │   ├── auth/
    │   │   ├── login.html              # Glassmorphism login
    │   │   └── register.html           # Password strength meter
    │   ├── dashboard/
    │   │   └── main.html               # KPIs + ECG + charts + vitals log
    │   ├── modules/
    │   │   ├── ai_doctor.html          # AI chat with orb + sessions
    │   │   ├── disease_detection.html  # 3-disease ML predictor
    │   │   ├── symptom_engine.html     # NLP symptom triage
    │   │   ├── mental_wellness.html    # Wellness assessment + gauge
    │   │   ├── hospital_locator.html   # Leaflet map + hospital cards
    │   │   ├── voice_assistant.html    # Waveform + speech-to-text
    │   │   ├── bmi_fitness.html        # BMI gauge + caloric needs
    │   │   ├── medicine_recommendation.html
    │   │   ├── health_analytics.html   # Plotly 3D + Chart.js
    │   │   ├── medical_reports.html    # PDF generator
    │   │   ├── health_timeline.html    # Visual timeline
    │   │   ├── emergency.html          # Critical alert system + CPR guide
    │   │   └── settings.html           # Theme + profile + security
    │   └── errors/
    │       ├── 404.html
    │       ├── 500.html
    │       └── 403.html
    └── static/
        ├── css/
        │   ├── nexus_core.css          # Design system + sidebar + navbar
        │   ├── animations.css          # GSAP + CSS animation library
        │   ├── landing.css             # Hero + features + pricing
        │   ├── dashboard.css           # KPI cards + ECG + grid
        │   ├── auth.css                # Glassmorphism auth cards
        │   ├── modules.css             # All module styles
        │   ├── ai_doctor.css           # Chat interface + AI orb
        │   └── emergency.css           # Siren + radar + alert styles
        └── js/
            ├── nexus_particles.js      # Canvas particle system
            ├── nexus_core.js           # ECG animator + GSAP + utils
            ├── landing.js              # Hero animations + landing charts
            ├── auth.js                 # Auth canvas + ECG
            ├── dashboard.js            # Chart.js + real-time KPIs + vitals log
            ├── ai_doctor.js            # Chat engine + voice input
            ├── disease_detection.js    # ML prediction UI + confidence gauge
            ├── mental_wellness.js      # Wellness gauge + assessment
            ├── hospital_locator.js     # Leaflet map + hospital cards
            ├── voice_assistant.js      # Web Speech API + waveform
            ├── health_analytics.js     # Plotly 3D + Chart.js analytics
            └── emergency.js            # Emergency detection + siren UI
```

---

## 🧠 AI Modules Summary

| Module | Algorithm | Accuracy | Features |
|--------|-----------|----------|----------|
| Diabetes Predictor | Random Forest (200 trees) | **90.0%** | 8 clinical params |
| Heart Disease | Gradient Boosting | **89.5%** | 10 cardiac params |
| Hypertension | Random Forest (150 trees) | **91.0%** | 7 lifestyle params |
| Symptom Engine | NLP keyword triage | — | 24 symptoms mapped |
| AI Doctor Chat | Knowledge base + NLP | — | 15+ medical topics |
| Medicine Engine | Evidence-based DB | — | 6 condition categories |
| Mental Wellness | Scoring algorithm | — | 3-axis assessment |
| Emergency Detector | Pattern matching | — | 6 emergency types |
| Report Generator | ReportLab PDF | — | Professional A4 format |

---

## 🎨 Design System

| Element | Value |
|---------|-------|
| Primary Color | `#00d4ff` (Neon Cyan) |
| Secondary | `#0066ff` (Electric Blue) |
| Accent | `#7c3aed` (Quantum Purple) |
| Background | `#020817` (Deep Space) |
| Font 1 | Orbitron (headings, labels) |
| Font 2 | Rajdhani (UI elements) |
| Font 3 | Inter (body text) |
| Charts | Chart.js 4.4 + Plotly 2.27 |
| Animations | GSAP 3.12 + CSS keyframes |
| Particles | Canvas 2D API |
| Maps | Leaflet.js 1.9 |
| Icons | Font Awesome 6.5 |

---

## 🔌 API Endpoints

```
GET  /api/v1/status              — Platform health check
GET  /api/v1/dashboard/kpis      — Live KPI metrics
GET  /api/v1/tips/random         — Random health tip
POST /api/v1/voice/parse         — Voice transcript analysis

POST /ai/predict-disease         — ML disease prediction
POST /ai/analyze-symptoms        — NLP symptom analysis
POST /ai/recommend-medicine      — Medicine recommendations
POST /ai/mental-health-assess    — Mental wellness scoring
POST /ai/log-vitals              — Save vital signs
POST /ai/bmi-analyze             — BMI + caloric analysis
GET  /ai/health-tips             — All health tips

GET  /analytics/health-trends    — Vital sign trends
GET  /analytics/risk-matrix      — Disease risk scores
GET  /analytics/wellness-score   — Wellness components
GET  /analytics/activity-feed    — Recent activity

POST /emergency/detect           — Emergency symptom detection
GET  /emergency/alerts/active    — Active emergency alerts

POST /hologram/chat/send         — AI Doctor message
GET  /hologram/chat/history/:id  — Chat session history
POST /hologram/hospitals/nearby  — Find nearby hospitals
POST /hologram/report/generate   — Generate PDF report

GET  /pulse/vitals/stream        — Vitals history stream
GET  /pulse/ecg/generate         — ECG waveform data
GET  /pulse/realtime/metrics     — Simulated real-time metrics
```

---

## 🔄 Retrain Models

```bash
# Generate fresh datasets
cd datasets && python generate_datasets.py && cd ..

# Retrain all models
python ai_engine/train_models.py
```

---

## 🚀 Production Deployment

```bash
# With gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# With Docker (create Dockerfile)
docker build -t medi-ai-nexus .
docker run -p 5000:5000 medi-ai-nexus
```

---

## ⚠️ Medical Disclaimer

This platform is for **educational and demonstration purposes only**. AI predictions, symptom analysis, and medical information provided are **not a substitute** for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional for medical decisions.

---

*Built with ❤️ — MEDI AI NEXUS v2.1.0 | The Future of Healthcare Intelligence*
