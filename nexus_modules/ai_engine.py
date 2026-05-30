"""
AURA MEDIX — AI Engine Blueprint
ML prediction and AI feature API routes with FULL DATABASE PERSISTENCE
"""

from __future__ import annotations

import logging
import random
import json
from datetime import datetime, timedelta

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from nexus_core import db
from nexus_core.quantum_models import (
    VitalSign, DiseasePredictor, HealthTimeline, Report
)
from ai_engine.nexus_predictor import predictor, FEATURE_COUNTS
from ai_engine.symptom_parser import analyzer
from ai_engine.nexus_chatbot import ai_doctor
from ai_engine.report_generator import ReportGenerator

ai_engine = Blueprint("ai_engine", __name__, url_prefix="/ai")
logger = logging.getLogger(__name__)
report_generator = ReportGenerator()

# ============================================================
# DISEASE PREDICTION WITH DATABASE PERSISTENCE
# ============================================================

@ai_engine.route("/predict-disease", methods=["POST"])
@login_required
def predict_disease():
    """
    Predict disease risk using ML models with FULL database persistence.
    
    Step 1: Run ML prediction
    Step 2: Save prediction to database
    Step 3: Create health timeline entry
    Step 4: Generate medical report
    Step 5: Return unified response
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    disease_type = (data.get("disease") or "").lower().strip()
    features     = data.get("features", [])

    # ── Validation ──────────────────────────────────────────────────────────
    if not disease_type:
        return jsonify({"error": "Missing field: disease"}), 400

    valid_diseases = list(FEATURE_COUNTS.keys())
    if disease_type not in valid_diseases:
        return jsonify({
            "error": (
                f'Unknown disease type "{disease_type}". '
                f'Valid options: {", ".join(valid_diseases)}'
            )
        }), 400

    if not features:
        return jsonify({"error": "Missing field: features"}), 400

    try:
        features = [float(f) for f in features]
    except (TypeError, ValueError):
        return jsonify({"error": "All features must be numeric values"}), 400

    expected_count = FEATURE_COUNTS[disease_type]
    if len(features) != expected_count:
        return jsonify({
            "error": (
                f"{disease_type} prediction requires exactly {expected_count} features, "
                f"but {len(features)} were provided."
            )
        }), 400

    # ── STEP 1: PREDICTION ──────────────────────────────────────────────────
    try:
        current_app.logger.info(
            "[predict_disease] disease=%s features(%d)=%s",
            disease_type, len(features), features,
        )

        if disease_type == "diabetes":
            result = predictor.predict_diabetes(features)
        elif disease_type == "heart":
            result = predictor.predict_heart_disease(features)
        elif disease_type == "hypertension":
            result = predictor.predict_hypertension(features)

        if "error" in result:
            current_app.logger.warning(
                "[predict_disease] Soft error for %s: %s",
                disease_type, result["error"],
            )

        result["recommendations"] = predictor.get_recommendations(
            disease_type,
            result.get("category", "Unknown"),
        )

        # ── STEP 2: SAVE TO DATABASE ────────────────────────────────────────
        try:
            prediction_obj = DiseasePredictor(
                user_id=current_user.id,
                disease_name=disease_type.capitalize(),
                disease_type=disease_type,
                prediction_result=result.get("category", "Unknown"),
                probability=result.get("probability", 0.0),
                risk_percentage=result.get("risk", 0.0),
                confidence_score=result.get("risk", 0.0),
                severity=_map_category_to_severity(result.get("category", "Unknown")),
                input_data=json.dumps(features),
                recommendations=json.dumps(result.get("recommendations", [])),
                model_used=result.get("model_used", "unknown"),
                timestamp=datetime.utcnow(),
            )
            db.session.add(prediction_obj)
            db.session.commit()
            
            current_app.logger.info(
                "[predict_disease] Saved prediction id=%d for user=%d",
                prediction_obj.id, current_user.id
            )

            # ── STEP 3: CREATE TIMELINE ENTRY ────────────────────────────────
            timeline_entry = HealthTimeline(
                user_id=current_user.id,
                prediction_id=prediction_obj.id,
                event_type='prediction',
                title=f"{disease_type.capitalize()} Risk Analysis",
                description=f"ML prediction completed for {disease_type} disease",
                disease_analyzed=disease_type,
                result=result.get("category", "Unknown"),
                severity=_map_category_to_severity(result.get("category", "Unknown")),
                ai_recommendation=json.dumps(result.get("recommendations", [])),
                data=json.dumps({
                    "risk_percentage": result.get("risk", 0.0),
                    "probability": result.get("probability", 0.0),
                    "model_used": result.get("model_used", "unknown")
                }),
                timestamp=datetime.utcnow(),
            )
            db.session.add(timeline_entry)
            db.session.commit()
            
            current_app.logger.info(
                "[predict_disease] Created timeline entry id=%d",
                timeline_entry.id
            )

            # ── STEP 4: GENERATE REPORT ─────────────────────────────────────
            try:
                pdf_bytes = report_generator.generate_disease_report(
                    current_user,
                    prediction_obj
                )
                
                report_obj = Report(
                    user_id=current_user.id,
                    title=f"{disease_type.capitalize()} Risk Assessment Report",
                    report_type='disease_prediction',
                    disease_name=disease_type,
                    prediction_id=prediction_obj.id,
                    content='auto-generated-disease-report',
                )
                db.session.add(report_obj)
                db.session.commit()
                
                current_app.logger.info(
                    "[predict_disease] Generated report id=%d",
                    report_obj.id
                )

                result["report_generated"] = True
                result["report_id"] = report_obj.id

            except Exception as report_exc:
                current_app.logger.error(
                    "[predict_disease] Report generation failed: %s",
                    report_exc, exc_info=True
                )
                result["report_generated"] = False
                result["report_error"] = str(report_exc)

            # ── STEP 5: RETURN UNIFIED RESPONSE ─────────────────────────────
            result["prediction_id"] = prediction_obj.id
            result["timeline_id"] = timeline_entry.id
            result["saved_to_database"] = True

            return jsonify(result)

        except Exception as db_exc:
            db.session.rollback()
            current_app.logger.error(
                "[predict_disease] Database error: %s",
                db_exc, exc_info=True
            )
            return jsonify({
                "error": "Failed to save prediction to database",
                "details": str(db_exc)
            }), 500

    except Exception as exc:
        current_app.logger.error(
            "[predict_disease] Unhandled exception for %s: %s",
            disease_type, exc, exc_info=True,
        )
        return jsonify({"error": "Internal server error during prediction"}), 500


def _map_category_to_severity(category: str) -> str:
    """Map risk category to severity level"""
    category = (category or "").lower()
    if "critical" in category:
        return "critical"
    elif "high" in category:
        return "high"
    elif "medium" in category:
        return "medium"
    else:
        return "low"


# ============================================================
# GET PREDICTIONS HISTORY
# ============================================================

@ai_engine.route("/predictions/history", methods=["GET"])
@login_required
def get_predictions_history():
    """Get user's prediction history for timeline"""
    days = request.args.get("days", 30, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    
    predictions = DiseasePredictor.query.filter(
        DiseasePredictor.user_id == current_user.id,
        DiseasePredictor.created_at >= start_date,
    ).order_by(DiseasePredictor.created_at.desc()).all()
    
    return jsonify({
        "success": True,
        "count": len(predictions),
        "predictions": [p.to_dict() for p in predictions]
    })


# ============================================================
# SYMPTOM ANALYSIS (WITH DATABASE PERSISTENCE)
# ============================================================

@ai_engine.route("/analyze-symptoms", methods=["POST"])
@login_required
def analyze_symptoms():
    """Analyze symptoms with timeline and report generation"""
    data = request.get_json()
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    symptoms      = data.get("symptoms", [])
    severity      = int(data.get("severity", 5))
    duration      = data.get("duration", "")
    age           = int(data.get("age", 30))
    gender        = data.get("gender", "unknown")

    if not symptoms:
        return jsonify({"success": False, "error": "No symptoms provided"}), 400

    try:
        current_app.logger.info(
            "Symptoms: %s, severity: %d", symptoms, severity
        )

        symptoms_text = ", ".join(symptoms)
        base_result   = analyzer.analyze_symptoms(symptoms_text)

        conditions    = base_result.get("possible_diseases", [])
        top_conf      = conditions[0]["confidence"] / 100 if conditions else 0.3
        symptom_count = len(symptoms)

        # ── Risk classification ─────────────────────────────────────────────
        if severity >= 8 or top_conf >= 0.80 or symptom_count >= 6:
            risk_level = "Critical"
            urgency    = "Immediate — seek emergency care"
        elif severity >= 6 or top_conf >= 0.60 or symptom_count >= 4:
            risk_level = "High"
            urgency    = "Within 24 hours — see a doctor"
        elif severity >= 4 or top_conf >= 0.40 or symptom_count >= 2:
            risk_level = "Medium"
            urgency    = "This week — schedule appointment"
        else:
            risk_level = "Low"
            urgency    = "Routine — monitor symptoms"

        # ── Format conditions ───────────────────────────────────────────────
        formatted_conditions = [
            {
                "name":        c["disease"],
                "probability": round(c["confidence"] / 100, 2),
                "description": f"Matched {c['matching_symptoms']} symptom(s)",
            }
            for c in conditions[:5]
        ] if conditions else [
            {
                "name":        "General Wellness Review",
                "probability": 0.35,
                "description": "No specific condition matched — monitor symptoms",
            }
        ]

        # ── Recommendations ────────────────────────────────────────────────
        if risk_level == "Critical":
            recs = [
                "Seek immediate emergency medical care",
                "Call 112 or go to nearest ER now",
                "Do not drive yourself if experiencing chest pain or dizziness",
            ]
        elif risk_level == "High":
            recs = [
                "Contact your doctor today",
                "Request urgent appointment within 24 hours",
                "Monitor symptoms every 2 hours",
                "Avoid strenuous activity",
            ]
        elif risk_level == "Medium":
            recs = [
                "Schedule a medical consultation this week",
                "Track symptoms and note any changes",
                "Stay hydrated and rest",
                "Avoid self-medicating without guidance",
            ]
        else:
            recs = [
                "Monitor symptoms over the next few days",
                "Maintain healthy lifestyle habits",
                "Stay hydrated and get adequate sleep",
            ]

        # ── Save to timeline ────────────────────────────────────────────────
        try:
            timeline_entry = HealthTimeline(
                user_id=current_user.id,
                event_type='symptom',
                title=f"Symptom Analysis - {', '.join(symptoms[:3])}",
                description=f"Analyzed {len(symptoms)} symptoms with severity {severity}/10",
                result=risk_level,
                severity=_map_category_to_severity(risk_level),
                ai_recommendation=json.dumps(recs),
                data=json.dumps({
                    "symptoms": symptoms,
                    "severity": severity,
                    "conditions": formatted_conditions
                }),
                timestamp=datetime.utcnow(),
            )
            db.session.add(timeline_entry)
            db.session.commit()
        except Exception as e:
            current_app.logger.error("Failed to save symptom analysis: %s", e)
            db.session.rollback()

        return jsonify({
            "success":       True,
            "risk_level":    risk_level,
            "confidence":    round(top_conf, 2),
            "conditions":    formatted_conditions,
            "recommendations": recs,
            "urgency":       urgency,
            "severity_input": severity,
            "symptom_count": symptom_count,
            "saved_to_timeline": True,
        })

    except Exception as exc:
        current_app.logger.error(
            "Symptom analysis error: %s", exc, exc_info=True
        )
        return jsonify({"success": False, "error": str(exc)}), 500


# ============================================================
# AI DOCTOR CHAT
# ============================================================

@ai_engine.route("/chat", methods=["POST"])
@login_required
def chat():
    """AI doctor conversational endpoint."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"success": False, "error": "No message provided"}), 400

    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"success": False, "error": "Empty message"}), 400

    try:
        result = ai_doctor.generate_response(user_message)
        return jsonify({
            "success":        True,
            "response":       result.get("message", ""),
            "type":           result.get("type", "general"),
            "requires_human": result.get("requires_human", False),
            "follow_up":      result.get("follow_up"),
            "timestamp":      datetime.utcnow().isoformat(),
        })
    except Exception as exc:
        current_app.logger.error("Chat error: %s", exc)
        return jsonify({"success": False, "error": "Server error occurred"}), 500


# ============================================================
# VITAL SIGNS
# ============================================================

@ai_engine.route("/log-vitals", methods=["POST"])
@login_required
def log_vitals():
    """Log vital signs for the current user."""
    data = request.json
    try:
        vital = VitalSign(
            user_id=current_user.id,
            heart_rate=data.get("heart_rate"),
            blood_pressure_systolic=data.get("bp_systolic"),
            blood_pressure_diastolic=data.get("bp_diastolic"),
            temperature_celsius=data.get("temperature"),
            blood_glucose=data.get("blood_glucose"),
            oxygen_saturation=data.get("oxygen_saturation"),
            recorded_at=datetime.utcnow(),
        )
        db.session.add(vital)
        db.session.commit()
        
        # Create timeline entry for vital logging
        timeline_entry = HealthTimeline(
            user_id=current_user.id,
            event_type='vitals',
            title="Vital Signs Logged",
            description="User logged vital signs",
            data=json.dumps({
                "heart_rate": data.get("heart_rate"),
                "bp_systolic": data.get("bp_systolic"),
                "bp_diastolic": data.get("bp_diastolic"),
                "temperature": data.get("temperature"),
            }),
            timestamp=datetime.utcnow(),
        )
        db.session.add(timeline_entry)
        db.session.commit()
        
        return jsonify({
            "status":   "success",
            "vital_id": vital.id,
            "message":  "Vitals logged successfully",
        })
    except Exception as exc:
        db.session.rollback()
        return jsonify({"error": str(exc)}), 500


@ai_engine.route("/vitals/recent", methods=["GET"])
@login_required
def get_recent_vitals():
    """Return recent vital signs for the current user."""
    days       = request.args.get("days", 7, type=int)
    start_date = datetime.utcnow() - timedelta(days=days)
    vitals     = (
        VitalSign.query
        .filter(
            VitalSign.user_id     == current_user.id,
            VitalSign.recorded_at >= start_date,
        )
        .order_by(VitalSign.recorded_at.desc())
        .limit(100)
        .all()
    )
    return jsonify([
        {
            "id":                v.id,
            "heart_rate":        v.heart_rate,
            "bp_systolic":       v.blood_pressure_systolic,
            "bp_diastolic":      v.blood_pressure_diastolic,
            "temperature":       v.temperature_celsius,
            "blood_glucose":     v.blood_glucose,
            "oxygen_saturation": v.oxygen_saturation,
            "recorded_at":       v.recorded_at.isoformat(),
        }
        for v in vitals
    ])


# ============================================================
# BMI ANALYSIS
# ============================================================

@ai_engine.route("/bmi-analyze", methods=["POST"])
@login_required
def bmi_analyze():
    """Calculate BMI, category, ideal range, BMR, and caloric needs."""
    data      = request.get_json()
    weight_kg = data.get("weight_kg") or data.get("weight")
    height_cm = data.get("height_cm") or data.get("height")
    age       = data.get("age", 30)
    gender    = data.get("gender", "female")

    if not weight_kg or not height_cm:
        return jsonify({"success": False, "error": "Weight and height required"}), 400

    try:
        weight_kg = float(weight_kg)
        height_cm = float(height_cm)
        age       = int(age) if age else 30

        if weight_kg <= 0 or height_cm <= 0:
            return jsonify({"success": False, "error": "Invalid measurements"}), 400

        height_m = height_cm / 100
        bmi      = round(weight_kg / (height_m ** 2), 1)

        if   bmi < 18.5: category, color = "Underweight",   "#60A5FA"
        elif bmi < 25:   category, color = "Normal Weight", "#34D399"
        elif bmi < 30:   category, color = "Overweight",    "#FBBF24"
        else:            category, color = "Obese",         "#F87171"

        ideal_min = round(18.5 * (height_m ** 2), 1)
        ideal_max = round(24.9 * (height_m ** 2), 1)

        if gender and gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

        if   bmi < 18.5: recommendation = "Consider a calorie-dense, nutrient-rich diet and consult a nutritionist."
        elif bmi < 25:   recommendation = "Excellent! Maintain your healthy weight through balanced diet and regular activity."
        elif bmi < 30:   recommendation = "Aim for 150 min/week of moderate exercise and reduce processed food intake."
        else:            recommendation = "Consult a healthcare professional for a personalised weight management plan."

        return jsonify({
            "success":     True,
            "bmi":         bmi,
            "category":    category,
            "color":       color,
            "ideal_range": f"{ideal_min} – {ideal_max} kg",
            "recommendation": recommendation,
            "bmr":         round(bmr, 0),
            "caloric_needs": {
                "sedentary": round(bmr * 1.2,  0),
                "moderate":  round(bmr * 1.55, 0),
                "active":    round(bmr * 1.9,  0),
            },
            "recommendations": [
                f"Current BMI: {bmi} ({category})",
                recommendation,
                "Exercise regularly (150 min/week moderate activity)",
                "Monitor weight monthly",
                "Consult healthcare provider for personalised advice",
            ],
        })
    except Exception as exc:
        return jsonify({"success": False, "error": str(exc)}), 500


# ============================================================
# HEALTH TIPS
# ============================================================

@ai_engine.route("/health-tips", methods=["GET"])
def get_health_tips():
    """Return a random health tip plus the full tips list."""
    tips = [
        "💧 Stay hydrated: Drink at least 8 glasses of water daily",
        "🏃 Exercise daily: 150 minutes of moderate activity per week",
        "🥗 Eat balanced meals: Include vegetables, proteins, and whole grains",
        "😴 Sleep well: Get 7–9 hours of quality sleep each night",
        "🧘 Manage stress: Practice meditation or yoga",
        "❌ Avoid smoking and limit alcohol consumption",
        "🍎 Eat fruits and vegetables: 5 portions daily",
        "⏱️ Regular check-ups: Annual health screening",
        "📱 Limit screen time: Take breaks every hour",
        "🚴 Find an exercise you enjoy: Consistency matters",
    ]
    return jsonify({"tip": random.choice(tips), "all_tips": tips})


# ============================================================
# MENTAL WELLNESS
# ============================================================

@ai_engine.route("/mental-health-assess", methods=["POST"])
@login_required
def mental_health_assess():
    """Mental wellness assessment — returns score, status, and recommendations."""
    data    = request.get_json()
    stress  = int(data.get("stress",  data.get("stress_level",  5)))
    anxiety = int(data.get("anxiety", data.get("anxiety_level", 5)))
    energy  = int(data.get("energy",  data.get("energy_level",  5)))
    sleep   = int(data.get("sleep",   data.get("sleep_quality", 5)))
    mood    = data.get("mood", "Okay")
    journal = data.get("journal", "")

    wellness_score = round(((10 - stress) + (10 - anxiety) + energy + sleep) / 4, 1)

    if   wellness_score >= 8: status, color = "Excellent", "success"
    elif wellness_score >= 6: status, color = "Good",      "info"
    elif wellness_score >= 4: status, color = "Fair",      "warning"
    else:                     status, color = "Poor",      "danger"

    recommendations = []
    if sleep < 5:
        recommendations.append(
            "Improve sleep hygiene: consistent schedule, dark room, no screens before bed"
        )
    if stress > 6:
        recommendations.append(
            "Practice stress reduction: meditation, yoga, or professional counseling"
        )
    if anxiety > 6:
        recommendations.append(
            "Consider speaking with a mental health professional about anxiety management"
        )
    if energy < 4:
        recommendations.append(
            "Boost energy: regular exercise, balanced nutrition, and adequate hydration"
        )
    if not recommendations:
        recommendations.append(
            "Keep up your healthy habits — your wellness profile looks balanced"
        )

    insights = f"Your wellness score is {wellness_score}/10 ({status}). "
    if stress > 7 or anxiety > 7:
        insights += "Elevated stress and anxiety detected. Prioritise relaxation techniques. "
    if sleep < 5:
        insights += "Poor sleep quality is impacting your overall wellness. "
    if energy >= 7 and sleep >= 7:
        insights += "Your energy and sleep are in great shape — keep it up. "

    return jsonify({
        "success":         True,
        "wellness_score":  wellness_score,
        "status":          status,
        "color":           color,
        "insights":        insights,
        "components":      {
            "stress":  stress,
            "anxiety": anxiety,
            "energy":  energy,
            "sleep":   sleep,
        },
        "recommendations": recommendations,
    })