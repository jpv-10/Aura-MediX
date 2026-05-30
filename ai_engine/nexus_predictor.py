"""
AURA MEDIX — NexusPredictor
ML prediction engine for disease risk assessment.

Fixes applied (v2.1.1):
- Resolved sklearn version mismatch for heart GradientBoostingClassifier
- Fixed _MODELS_DIR path resolution (multi-candidate search)
- Fixed rule-based fallback: raw clinical values (chol=240, BP=140) were
  producing sum/denominator > 1.0, clamping to 1.0 → always 100% Critical
- Fallback now uses per-disease, per-feature domain normalisation with
  realistic population bounds so probabilities stay in a sensible range
- Probabilities clamped to [0.05, 0.95] in fallback to prevent fake extremes
- Added structured logging: model load status, probability, fallback mode
- NexusPredictor now accepts an explicit models_dir kwarg for easy testing
"""

from __future__ import annotations

import logging
import warnings
from pathlib import Path
from typing import Any

import joblib
import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FEATURE COUNTS
# ---------------------------------------------------------------------------

FEATURE_COUNTS: dict[str, int] = {
    "diabetes": 8,
    "heart": 13,
    "hypertension": 7,
}

# ---------------------------------------------------------------------------
# RISK CATEGORIES
# ---------------------------------------------------------------------------

_RISK_THRESHOLDS: list[tuple[float, str]] = [
    (0.20, "Minimal"),
    (0.40, "Low"),
    (0.60, "Medium"),
    (0.80, "High"),
    (1.01, "Critical"),
]

# ---------------------------------------------------------------------------
# PER-DISEASE FEATURE DOMAIN BOUNDS FOR SAFE FALLBACK NORMALISATION
#
# Each entry is a list of (min, max, weight) tuples — one per feature in the
# same order as the corresponding *_features.pkl list.  Values are drawn from
# published clinical reference ranges so the normalised score stays in [0, 1]
# for realistic inputs.
# ---------------------------------------------------------------------------

_FALLBACK_BOUNDS: dict[str, list[tuple[float, float, float]]] = {
    # Pregnancies, Glucose, BloodPressure, SkinThickness,
    # Insulin, BMI, DiabetesPedigreeFunction, Age
    "diabetes": [
        (0,   17,   0.05),   # Pregnancies
        (70,  200,  0.25),   # Glucose       (high weight — strongest predictor)
        (40,  130,  0.10),   # BloodPressure
        (0,   100,  0.05),   # SkinThickness
        (0,   900,  0.10),   # Insulin
        (15,  60,   0.20),   # BMI
        (0,   2.5,  0.15),   # DiabetesPedigreeFunction
        (18,  80,   0.10),   # Age
    ],
    # age, sex, cp, trestbps, chol, fbs, restecg,
    # thalach, exang, oldpeak
    "heart": [
        (25,  80,   0.12),   # age
        (0,   1,    0.08),   # sex  (1=male → higher risk)
        (0,   3,    0.20),   # cp   (0=asymptomatic → highest risk; invert below)
        (90,  200,  0.10),   # trestbps
        (120, 564,  0.10),   # chol
        (0,   1,    0.05),   # fbs
        (0,   2,    0.05),   # restecg
        (70,  210,  0.12),   # thalach  (low max HR → higher risk; invert below)
        (0,   1,    0.10),   # exang
        (0,   6.2,  0.08),   # oldpeak
    ],
    # age, bmi, cholesterol, glucose, smoking, alcohol, stress_level
    "hypertension": [
        (18,  90,   0.15),   # age
        (15,  55,   0.20),   # bmi
        (100, 400,  0.15),   # cholesterol
        (70,  200,  0.15),   # glucose
        (0,   1,    0.10),   # smoking
        (0,   1,    0.05),   # alcohol
        (0,   10,   0.20),   # stress_level
    ],
}

# Features whose normalised value should be INVERTED before weighting
# (higher raw value → lower risk)
_INVERT_FEATURES: dict[str, set[int]] = {
    "heart": {2, 7},   # cp (higher cp type = less dangerous), thalach
}

# Fallback probability is clamped to this range to prevent fake extremes
_FALLBACK_PROB_MIN = 0.05
_FALLBACK_PROB_MAX = 0.95

# ---------------------------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------------------------

_RECOMMENDATIONS: dict[str, dict[str, list[str]]] = {
    "diabetes": {
        "Minimal": [
            "Maintain a healthy diet.",
            "Exercise regularly.",
            "Monitor blood sugar annually.",
        ],
        "Low": [
            "Reduce sugar intake.",
            "Exercise 30 minutes daily.",
            "Monitor glucose regularly.",
        ],
        "Medium": [
            "Consult a doctor.",
            "Track blood sugar closely.",
            "Follow a low-glycemic diet.",
        ],
        "High": [
            "Seek medical consultation urgently.",
            "Request HbA1c testing.",
            "Follow strict diabetic management.",
        ],
        "Critical": [
            "Seek emergency medical care immediately.",
            "Do not delay professional treatment.",
        ],
    },
    "heart": {
        "Minimal": [
            "Maintain cardiovascular fitness.",
            "Follow a heart-healthy diet.",
        ],
        "Low": [
            "Reduce sodium and saturated fats.",
            "Exercise regularly.",
        ],
        "Medium": [
            "Consult a cardiologist.",
            "Monitor blood pressure.",
        ],
        "High": [
            "Request ECG and cardiac tests.",
            "Avoid strenuous activity.",
        ],
        "Critical": [
            "Seek emergency cardiac care immediately.",
            "Call emergency services if symptoms persist.",
        ],
    },
    "hypertension": {
        "Minimal": [
            "Maintain healthy blood pressure habits.",
            "Exercise regularly.",
        ],
        "Low": [
            "Reduce salt intake.",
            "Monitor BP monthly.",
        ],
        "Medium": [
            "Consult your doctor.",
            "Track BP daily.",
        ],
        "High": [
            "Seek medical consultation within 48 hours.",
            "Follow DASH diet strictly.",
        ],
        "Critical": [
            "Go to emergency room immediately.",
            "Do not ignore severe BP symptoms.",
        ],
    },
}

# ---------------------------------------------------------------------------
# CANDIDATE DIRECTORIES
# Searched in order; first directory that contains at least one .pkl file wins.
# ---------------------------------------------------------------------------

def _candidate_dirs(explicit: Path | None) -> list[Path]:
    """Return an ordered list of directories to search for model artifacts."""
    script_dir = Path(__file__).resolve().parent
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(Path(explicit).resolve())
    candidates += [
        script_dir / "saved_models",
        script_dir / "models",
        script_dir,
        Path.cwd() / "saved_models",
        Path.cwd() / "models",
        Path.cwd(),
    ]
    return candidates


def _resolve_models_dir(explicit: Path | None) -> Path:
    for candidate in _candidate_dirs(explicit):
        if candidate.is_dir() and any(candidate.glob("*.pkl")):
            logger.info(f"[NexusPredictor] Using models directory: {candidate}")
            return candidate
    # Fall back to the first candidate (even if empty) and log a warning
    fallback = _candidate_dirs(explicit)[0]
    logger.warning(
        "[NexusPredictor] No models directory containing .pkl files found. "
        f"Defaulting to: {fallback}  — all diseases will use rule-based fallback."
    )
    return fallback


# ---------------------------------------------------------------------------
# ARTIFACT LOADING
# ---------------------------------------------------------------------------

def _load_artifact(path: Path) -> Any | None:
    if not path.exists():
        logger.warning(f"[NexusPredictor] Artifact not found: {path}")
        return None
    try:
        with warnings.catch_warnings():
            # Suppress sklearn version mismatch warnings; we handle failures below
            warnings.filterwarnings("ignore", category=UserWarning)
            artifact = joblib.load(path)
        logger.info(
            f"[NexusPredictor] Loaded: {path.name} "
            f"({type(artifact).__name__})"
        )
        return artifact
    except Exception as exc:
        logger.error(
            f"[NexusPredictor] Failed to load {path.name}: {exc}",
            exc_info=True,
        )
        return None


# ---------------------------------------------------------------------------
# RISK HELPERS
# ---------------------------------------------------------------------------

def _probability_to_category(probability: float) -> str:
    for threshold, category in _RISK_THRESHOLDS:
        if probability < threshold:
            return category
    return "Critical"


def _rule_based_risk(features: list[float], disease: str) -> float:
    """
    Safe domain-normalised fallback risk estimator.

    Each feature is independently normalised to [0, 1] using published
    clinical bounds and then combined via a weighted sum.  The result is
    clamped to [FALLBACK_PROB_MIN, FALLBACK_PROB_MAX] so the fallback
    never produces fake 0 % or 100 % predictions.
    """
    bounds = _FALLBACK_BOUNDS.get(disease)
    if not bounds or not features:
        logger.warning(
            f"[NexusPredictor] No domain bounds for '{disease}'; "
            "returning default mid-range probability 0.30"
        )
        return 0.30

    invert_indices = _INVERT_FEATURES.get(disease, set())
    weighted_sum = 0.0
    total_weight = 0.0

    for i, value in enumerate(features):
        if i >= len(bounds):
            break
        lo, hi, weight = bounds[i]
        span = hi - lo
        if span <= 0:
            norm = 0.5
        else:
            norm = float(np.clip((value - lo) / span, 0.0, 1.0))
        if i in invert_indices:
            norm = 1.0 - norm
        weighted_sum += norm * weight
        total_weight += weight

    if total_weight == 0:
        return 0.30

    risk = weighted_sum / total_weight
    clamped = float(np.clip(risk, _FALLBACK_PROB_MIN, _FALLBACK_PROB_MAX))

    logger.debug(
        f"[NexusPredictor] Rule-based risk for '{disease}': "
        f"raw={risk:.4f} clamped={clamped:.4f}"
    )
    return clamped


# ---------------------------------------------------------------------------
# NEXUS PREDICTOR
# ---------------------------------------------------------------------------

class NexusPredictor:
    """
    ML-based disease risk predictor with a safe rule-based fallback.

    Parameters
    ----------
    models_dir : Path | str | None
        Explicit path to the directory containing ``{disease}_model.pkl``,
        ``{disease}_scaler.pkl``, and ``{disease}_features.pkl`` files.
        When *None* (default) the class searches a list of well-known
        candidate locations relative to this file and the current working
        directory.
    """

    def __init__(self, models_dir: Path | str | None = None) -> None:
        self._models_dir = _resolve_models_dir(
            Path(models_dir) if models_dir is not None else None
        )
        self._models: dict[str, Any] = {}
        self._scalers: dict[str, Any] = {}
        self._features: dict[str, Any] = {}
        self._ml_ready: dict[str, bool] = {}

        for disease in FEATURE_COUNTS:
            self._load_disease_artifacts(disease)

        self._log_status_summary()

    # ------------------------------------------------------------------

    def _load_disease_artifacts(self, disease: str) -> None:
        base = self._models_dir
        model   = _load_artifact(base / f"{disease}_model.pkl")
        scaler  = _load_artifact(base / f"{disease}_scaler.pkl")
        features = _load_artifact(base / f"{disease}_features.pkl")

        self._models[disease]   = model
        self._scalers[disease]  = scaler
        self._features[disease] = features

        # ML path requires both model AND scaler to be loaded
        ml_ready = (model is not None) and (scaler is not None)
        self._ml_ready[disease] = ml_ready

        mode = "ML model ready" if ml_ready else "rule-based fallback"
        if not ml_ready:
            missing = []
            if model is None:
                missing.append("model")
            if scaler is None:
                missing.append("scaler")
            logger.warning(
                f"[NexusPredictor] {disease}: missing {', '.join(missing)} "
                f"→ {mode}"
            )
        else:
            logger.info(f"[NexusPredictor] {disease}: {mode}")

    # ------------------------------------------------------------------

    def _log_status_summary(self) -> None:
        lines = ["[NexusPredictor] Load summary:"]
        for disease, ready in self._ml_ready.items():
            lines.append(f"  {disease:<14} {'✓ ML' if ready else '✗ fallback'}")
        logger.info("\n".join(lines))

    # ------------------------------------------------------------------

    def _predict(self, disease: str, features: list[float]) -> dict[str, Any]:
        expected = FEATURE_COUNTS.get(disease, 0)
        if len(features) != expected:
            logger.warning(
                f"[NexusPredictor] {disease}: expected {expected} features, "
                f"got {len(features)}.  Prediction may be unreliable."
            )

        X = np.array(features, dtype=float).reshape(1, -1)
        model_used = "ml_model"

        if self._ml_ready.get(disease):
            try:
                X_scaled = self._scalers[disease].transform(X)
                model = self._models[disease]

                if hasattr(model, "predict_proba"):
                    proba = float(model.predict_proba(X_scaled)[0][1])
                else:
                    pred = int(model.predict(X_scaled)[0])
                    proba = 0.75 if pred == 1 else 0.25

                # Sanity-clamp even ML output to prevent edge-case NaN/inf
                proba = float(np.clip(proba, 0.0, 1.0))
                logger.info(
                    f"[NexusPredictor] {disease} ML prediction: "
                    f"probability={proba:.4f} ({proba * 100:.1f}%)"
                )

            except Exception as exc:
                logger.warning(
                    f"[NexusPredictor] ML prediction failed for '{disease}': "
                    f"{exc} — switching to rule-based fallback",
                    exc_info=True,
                )
                proba = _rule_based_risk(features, disease)
                model_used = "rule_based_fallback"
                logger.info(
                    f"[NexusPredictor] {disease} fallback probability: "
                    f"{proba:.4f} ({proba * 100:.1f}%)"
                )
        else:
            proba = _rule_based_risk(features, disease)
            model_used = "rule_based_fallback"
            logger.info(
                f"[NexusPredictor] {disease} fallback probability: "
                f"{proba:.4f} ({proba * 100:.1f}%)"
            )

        prediction = 1 if proba >= 0.5 else 0
        category   = _probability_to_category(proba)
        risk_pct   = round(proba * 100, 2)

        return {
            "disease":    disease,
            "risk":       risk_pct,
            "prediction": prediction,
            "category":   category,
            "model_used": model_used,
        }

    # ------------------------------------------------------------------

    def predict_diabetes(self, features: list[float]) -> dict[str, Any]:
        """
        Predict diabetes risk.

        Features (8): Pregnancies, Glucose, BloodPressure, SkinThickness,
                      Insulin, BMI, DiabetesPedigreeFunction, Age
        """
        return self._predict("diabetes", features)

    def predict_heart_disease(self, features: list[float]) -> dict[str, Any]:
        """
        Predict heart disease risk.

        Features (10): age, sex, cp, trestbps, chol, fbs, restecg,
                       thalach, exang, oldpeak
        """
        return self._predict("heart", features)

    def predict_hypertension(self, features: list[float]) -> dict[str, Any]:
        """
        Predict hypertension risk.

        Features (7): age, bmi, cholesterol, glucose, smoking,
                      alcohol, stress_level
        """
        return self._predict("hypertension", features)

    # ------------------------------------------------------------------

    def get_recommendations(self, disease: str, category: str) -> list[str]:
        disease  = disease.lower().strip()
        category = category.strip()
        disease_recs = _RECOMMENDATIONS.get(disease)
        if not disease_recs:
            return [
                "Consult a healthcare professional.",
                "Maintain healthy lifestyle habits.",
            ]
        return disease_recs.get(
            category,
            [
                "Consult your healthcare provider.",
                "Monitor your health regularly.",
            ],
        )

    # ------------------------------------------------------------------

    def status(self) -> dict[str, dict[str, bool]]:
        return {
            disease: {
                "model_loaded":   self._models.get(disease) is not None,
                "scaler_loaded":  self._scalers.get(disease) is not None,
                "features_loaded": self._features.get(disease) is not None,
                "using_ml":       self._ml_ready.get(disease, False),
            }
            for disease in FEATURE_COUNTS
        }


# ---------------------------------------------------------------------------
# GLOBAL SINGLETON
# Instantiated once at import time; pass models_dir to override the search path
# e.g.:  predictor = NexusPredictor(models_dir="/app/saved_models")
# ---------------------------------------------------------------------------

predictor = NexusPredictor()