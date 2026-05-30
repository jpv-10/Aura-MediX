"""
AURA MEDIX — REST API v1
Main API endpoints for external integrations
"""
from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from nexus_core.quantum_models import User, VitalSign
from ai_engine.report_generator import ReportGenerator
from datetime import datetime, timedelta
import random
import io

nexus_api = Blueprint('nexus_api', __name__, url_prefix='/api/v1')

report_generator = ReportGenerator()

# ==================== HEALTH CHECK ====================

@nexus_api.route('/status', methods=['GET'])
def api_status():
    """API health check"""
    return jsonify({
        'status': 'operational',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'AURA MEDIX'
    })

# ==================== DASHBOARD ====================

@nexus_api.route('/dashboard/kpis', methods=['GET'])
@login_required
def get_kpis():
    """Get dashboard KPIs"""
    recent = VitalSign.query.filter_by(
        user_id=current_user.id
    ).order_by(VitalSign.recorded_at.desc()).first()

    kpis = {
        'health_score': random.randint(65, 95),
        'vitals_tracked': VitalSign.query.filter_by(user_id=current_user.id).count(),
        'wellness_streak': random.randint(1, 30),
        'ai_insights': random.randint(3, 8),
        'current_vitals': {
            'heart_rate': recent.heart_rate if recent else 72,
            'blood_pressure': f"{recent.blood_pressure_systolic if recent else 120}/{recent.blood_pressure_diastolic if recent else 80}",
            'oxygen': f"{recent.oxygen_saturation if recent else 98}%",
            'temperature': f"{recent.temperature_celsius if recent else 37.0}°C"
        }
    }

    return jsonify(kpis)

# ==================== RANDOM TIPS ====================

@nexus_api.route('/tips/random', methods=['GET'])
def random_tip():
    """Get random health tip"""
    tips = [
        'Start your day with a glass of water',
        'Eat more vegetables and whole grains',
        'Exercise for at least 30 minutes daily',
        'Maintain consistent sleep schedule',
        'Practice mindfulness meditation',
        'Avoid excessive screen time',
        'Eat colorful foods (rainbow diet)',
        'Strength train 2-3 times per week',
        'Take regular walks after meals',
        'Practice gratitude daily'
    ]

    return jsonify({'tip': random.choice(tips)})

# ==================== VOICE PARSING ====================

@nexus_api.route('/voice/parse', methods=['POST'])
@login_required
def parse_voice():
    """Parse voice transcript"""
    data = request.json
    transcript = data.get('transcript', '')

    vitals = {}

    if 'heart rate' in transcript.lower():
        import re
        match = re.search(r'(\d+)\s*(?:bpm|beats)', transcript)
        if match:
            vitals['heart_rate'] = int(match.group(1))

    if 'blood pressure' in transcript.lower():
        import re
        match = re.search(r'(\d+)\s*(?:over|\/)\s*(\d+)', transcript)
        if match:
            vitals['bp_systolic'] = int(match.group(1))
            vitals['bp_diastolic'] = int(match.group(2))

    return jsonify({
        'transcript': transcript,
        'extracted_vitals': vitals,
        'confidence': 0.85
    })

# ==================== USER INFO ====================

@nexus_api.route('/user/profile', methods=['GET'])
@login_required
def get_user_profile():
    """Get user profile"""
    user = current_user
    profile = user.profile

    return jsonify({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'full_name': user.full_name,
        'profile': {
            'age': profile.age if profile else None,
            'gender': profile.gender if profile else None,
            'height_cm': profile.height_cm if profile else None,
            'weight_kg': profile.weight_kg if profile else None,
            'blood_type': profile.blood_type if profile else None
        },
        'created_at': user.created_at.isoformat()
    })

# ==================== PDF REPORT DOWNLOAD ====================

@nexus_api.route('/reports/download', methods=['GET'])
@nexus_api.route('/reports/download/<report_type>', methods=['GET'])
@login_required
def download_report(report_type: str = 'health_summary'):
    """
    Generate and stream a PDF health report.
    Opens inline in browser — change as_attachment=True to force download.

    Usage:
      GET /api/v1/reports/download
      GET /api/v1/reports/download/health_summary
      GET /api/v1/reports/download/vitals
    """
    try:
        pdf_bytes = report_generator.generate(current_user, report_type)
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)
        filename = f"aura_medix_{report_type}_{current_user.id}.pdf"

        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=filename,
        )

    except Exception as exc:
        from flask import current_app
        current_app.logger.error("PDF generation failed: %s", exc, exc_info=True)
        return jsonify({'error': 'PDF generation failed'}), 500

# ==================== MEDICINE RECOMMENDATION ====================

MEDICINE_DB = [
    {'name':'Metformin','generic_name':'Metformin HCl','drug_class':'Biguanide','condition':'Diabetes Type 2','dosage':'500-2000 mg/day','description':'First-line medication for type 2 diabetes. Reduces hepatic glucose production.','side_effects':['Nausea','Diarrhea','Stomach upset'],'contraindications':['Kidney disease','Liver disease','Alcohol abuse']},
    {'name':'Lisinopril','generic_name':'Lisinopril','drug_class':'ACE Inhibitor','condition':'Hypertension, Heart Failure','dosage':'5-40 mg/day','description':'Lowers blood pressure by relaxing blood vessels.','side_effects':['Dry cough','Dizziness','Headache'],'contraindications':['Pregnancy','Angioedema history','Bilateral renal artery stenosis']},
    {'name':'Atorvastatin','generic_name':'Atorvastatin Calcium','drug_class':'Statin','condition':'High Cholesterol, Heart Disease','dosage':'10-80 mg/day','description':'Reduces LDL cholesterol and triglycerides.','side_effects':['Muscle pain','Liver enzyme elevation','Headache'],'contraindications':['Liver disease','Pregnancy','Breastfeeding']},
    {'name':'Amlodipine','generic_name':'Amlodipine Besylate','drug_class':'Calcium Channel Blocker','condition':'Hypertension, Angina','dosage':'5-10 mg/day','description':'Relaxes blood vessels and reduces heart workload.','side_effects':['Ankle swelling','Flushing','Fatigue'],'contraindications':['Severe aortic stenosis','Cardiogenic shock']},
    {'name':'Omeprazole','generic_name':'Omeprazole','drug_class':'Proton Pump Inhibitor','condition':'GERD, Peptic Ulcer','dosage':'20-40 mg/day','description':'Reduces stomach acid production.','side_effects':['Headache','Nausea','Diarrhea'],'contraindications':['Hypersensitivity to PPIs']},
    {'name':'Sertraline','generic_name':'Sertraline HCl','drug_class':'SSRI','condition':'Depression, Anxiety','dosage':'50-200 mg/day','description':'Increases serotonin levels to improve mood and reduce anxiety.','side_effects':['Nausea','Insomnia','Sexual dysfunction'],'contraindications':['MAO inhibitor use','Pimozide use']},
    {'name':'Salbutamol','generic_name':'Albuterol','drug_class':'Beta-2 Agonist','condition':'Asthma, COPD','dosage':'2-4 puffs as needed','description':'Bronchodilator that relaxes airway muscles for quick relief.','side_effects':['Tremor','Palpitations','Headache'],'contraindications':['Hypersensitivity to albuterol']},
    {'name':'Ibuprofen','generic_name':'Ibuprofen','drug_class':'NSAID','condition':'Pain, Inflammation, Fever','dosage':'200-800 mg every 6-8h','description':'Anti-inflammatory analgesic for pain and fever relief.','side_effects':['Stomach upset','GI bleeding risk','Kidney stress'],'contraindications':['Peptic ulcer','Kidney disease','Third trimester pregnancy']},
    {'name':'Levothyroxine','generic_name':'Levothyroxine Sodium','drug_class':'Thyroid Hormone','condition':'Hypothyroidism','dosage':'25-200 mcg/day','description':'Replaces or supplements thyroid hormone.','side_effects':['Palpitations if overdosed','Weight loss','Insomnia'],'contraindications':['Untreated adrenal insufficiency','Thyrotoxicosis']},
    {'name':'Cetirizine','generic_name':'Cetirizine HCl','drug_class':'Antihistamine','condition':'Allergies, Urticaria','dosage':'10 mg/day','description':'Second-generation antihistamine with minimal sedation.','side_effects':['Drowsiness','Dry mouth','Headache'],'contraindications':['Severe kidney disease']},
]

@nexus_api.route('/medicines', methods=['GET'])
@login_required
def get_medicines():
    """Search medicine recommendations"""
    query = request.args.get('q', '').lower().strip()
    conditions = request.args.getlist('condition')

    results = MEDICINE_DB
    if query:
        results = [m for m in results if query in m['name'].lower() or query in m['condition'].lower() or query in m['drug_class'].lower()]
    if conditions:
        results = [m for m in results if any(c.lower() in m['condition'].lower() for c in conditions)]

    return jsonify({'success': True, 'medications': results[:10]})

@nexus_api.route('/medicine-recommend', methods=['POST'])
@login_required
def medicine_recommend():
    """Get medicine recommendations by condition"""
    data = request.get_json() or {}
    query = (data.get('query') or '').lower().strip()
    conditions = data.get('conditions', [])

    results = MEDICINE_DB
    if query:
        results = [m for m in results if query in m['name'].lower() or query in m['condition'].lower() or query in m['drug_class'].lower()]
    if conditions:
        filtered = [m for m in results if any(c.lower() in m['condition'].lower() for c in conditions)]
        if filtered:
            results = filtered

    return jsonify({'success': True, 'medications': results[:8]})

# ==================== FITNESS PLAN ====================

@nexus_api.route('/fitness-plan', methods=['POST'])
@login_required
def fitness_plan():
    """Generate a weekly fitness plan"""
    data = request.get_json() or {}
    goal  = data.get('goal', 'general')
    level = data.get('level', 'beginner')
    days  = min(int(data.get('days_per_week', 3)), 7)

    plans = {
        'lose_weight': {'beginner': [
            {'day':'Mon','workout':'Brisk Walk 30min','calories':200},
            {'day':'Wed','workout':'Cycling 25min + Core 10min','calories':280},
            {'day':'Fri','workout':'Swimming or Aqua aerobics 30min','calories':300},
            {'day':'Sat','workout':'Light Jog 20min + Stretching','calories':220},
        ]},
        'build_muscle': {'beginner': [
            {'day':'Mon','workout':'Upper Body - Push-ups, Rows, Shoulder Press','calories':250},
            {'day':'Wed','workout':'Lower Body - Squats, Lunges, Calf Raises','calories':270},
            {'day':'Fri','workout':'Full Body - Deadlifts, Pull-ups, Planks','calories':300},
            {'day':'Sun','workout':'Active Recovery - Yoga or Light Walk','calories':120},
        ]},
        'general': {'beginner': [
            {'day':'Mon','workout':'Walk 20min + Stretching 10min','calories':150},
            {'day':'Thu','workout':'Yoga or Pilates 30min','calories':180},
            {'day':'Sat','workout':'Light Jog 20min + Bodyweight exercises','calories':220},
        ]},
    }

    plan = plans.get(goal, plans['general']).get(level, plans['general']['beginner'])
    selected = plan[:days]

    return jsonify({
        'success': True,
        'plan': selected,
        'weekly_calories': sum(p['calories'] for p in selected),
        'tips': [
            'Warm up for 5 minutes before every session',
            'Stay hydrated - drink 500ml water before working out',
            'Rest at least one day between strength training sessions',
            'Track your progress weekly to stay motivated'
        ]
    })

# ==================== ERROR RESPONSES ====================

@nexus_api.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint not found'}), 404

@nexus_api.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@nexus_api.errorhandler(401)
def unauthorized(e):
    return jsonify({'error': 'Unauthorized access'}), 401