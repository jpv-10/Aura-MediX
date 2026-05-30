"""
AURA MEDIX — Medicine Recommendation Engine
Evidence-based pharmaceutical guidance system
"""

MEDICINE_DATABASE = {
    'diabetes': {
        'first_line': [
            {'name': 'Metformin', 'class': 'Biguanide', 'dose': '500-2000mg/day', 'notes': 'First-line for T2DM. Take with meals.', 'side_effects': 'GI upset, B12 deficiency'},
            {'name': 'Empagliflozin', 'class': 'SGLT-2 Inhibitor', 'dose': '10-25mg/day', 'notes': 'Cardiovascular and renal protective.', 'side_effects': 'UTI risk, genital infections'},
        ],
        'second_line': [
            {'name': 'Sitagliptin', 'class': 'DPP-4 Inhibitor', 'dose': '100mg/day', 'notes': 'Weight neutral, low hypoglycemia risk.', 'side_effects': 'Nasopharyngitis'},
            {'name': 'Semaglutide', 'class': 'GLP-1 Agonist', 'dose': '0.5-1mg/week', 'notes': 'Weight loss benefit, cardiovascular protection.', 'side_effects': 'Nausea, vomiting'},
        ],
        'lifestyle': ['Mediterranean diet', 'Aerobic exercise 150 min/week', 'Weight loss if overweight', 'Blood glucose monitoring']
    },
    'hypertension': {
        'first_line': [
            {'name': 'Amlodipine', 'class': 'Calcium Channel Blocker', 'dose': '5-10mg/day', 'notes': 'Well-tolerated, once daily dosing.', 'side_effects': 'Ankle edema, flushing'},
            {'name': 'Lisinopril', 'class': 'ACE Inhibitor', 'dose': '10-40mg/day', 'notes': 'Renal protective, preferred in diabetes.', 'side_effects': 'Dry cough, hyperkalemia'},
        ],
        'second_line': [
            {'name': 'Losartan', 'class': 'ARB', 'dose': '50-100mg/day', 'notes': 'Alternative to ACE inhibitors.', 'side_effects': 'Dizziness, hyperkalemia'},
            {'name': 'Hydrochlorothiazide', 'class': 'Thiazide Diuretic', 'dose': '12.5-25mg/day', 'notes': 'Often used in combination.', 'side_effects': 'Hypokalemia, hyperuricemia'},
        ],
        'lifestyle': ['DASH diet', 'Sodium restriction < 2300mg/day', 'Regular aerobic exercise', 'Limit alcohol', 'Stress management']
    },
    'heart_disease': {
        'first_line': [
            {'name': 'Aspirin', 'class': 'Antiplatelet', 'dose': '75-100mg/day', 'notes': 'Secondary prevention of MI/stroke.', 'side_effects': 'GI bleeding risk'},
            {'name': 'Atorvastatin', 'class': 'Statin', 'dose': '20-80mg/day', 'notes': 'LDL reduction, plaque stabilization.', 'side_effects': 'Myopathy, elevated liver enzymes'},
        ],
        'second_line': [
            {'name': 'Bisoprolol', 'class': 'Beta Blocker', 'dose': '2.5-10mg/day', 'notes': 'Heart rate control, post-MI protection.', 'side_effects': 'Bradycardia, fatigue'},
            {'name': 'Ramipril', 'class': 'ACE Inhibitor', 'dose': '2.5-10mg/day', 'notes': 'Reduces mortality post-MI.', 'side_effects': 'Dry cough, hypotension'},
        ],
        'lifestyle': ['Cardiac rehabilitation', 'Mediterranean diet', 'Smoking cessation', 'Weight management', 'Stress reduction']
    },
    'anxiety': {
        'first_line': [
            {'name': 'Sertraline', 'class': 'SSRI', 'dose': '50-200mg/day', 'notes': 'First-line for anxiety disorders.', 'side_effects': 'Initial anxiety increase, sexual dysfunction'},
            {'name': 'Escitalopram', 'class': 'SSRI', 'dose': '10-20mg/day', 'notes': 'Well-tolerated, fewer interactions.', 'side_effects': 'Nausea, insomnia'},
        ],
        'second_line': [
            {'name': 'Buspirone', 'class': 'Anxiolytic', 'dose': '15-60mg/day', 'notes': 'Non-addictive, for GAD.', 'side_effects': 'Dizziness, headache'},
            {'name': 'Venlafaxine', 'class': 'SNRI', 'dose': '75-225mg/day', 'notes': 'Effective for anxiety and depression.', 'side_effects': 'Hypertension, withdrawal effects'},
        ],
        'lifestyle': ['CBT therapy', 'Mindfulness meditation', 'Regular exercise', 'Sleep hygiene', 'Limit caffeine/alcohol']
    },
    'fever': {
        'first_line': [
            {'name': 'Paracetamol', 'class': 'Analgesic/Antipyretic', 'dose': '500-1000mg every 6-8h', 'notes': 'Safe for most patients. Max 4g/day.', 'side_effects': 'Hepatotoxicity in overdose'},
            {'name': 'Ibuprofen', 'class': 'NSAID', 'dose': '400mg every 8h with food', 'notes': 'Anti-inflammatory, antipyretic.', 'side_effects': 'GI irritation, renal effects'},
        ],
        'second_line': [],
        'lifestyle': ['Rest', 'Adequate hydration (2-3L/day)', 'Cool compresses', 'Light clothing']
    },
    'headache': {
        'first_line': [
            {'name': 'Paracetamol', 'class': 'Analgesic', 'dose': '500-1000mg as needed', 'notes': 'First choice for tension headache.', 'side_effects': 'Hepatotoxicity in overdose'},
            {'name': 'Ibuprofen', 'class': 'NSAID', 'dose': '400mg with food', 'notes': 'Effective for tension and migraine.', 'side_effects': 'GI irritation'},
        ],
        'second_line': [
            {'name': 'Sumatriptan', 'class': 'Triptan', 'dose': '50-100mg at onset', 'notes': 'Specific for migraine attacks.', 'side_effects': 'Chest tightness, flushing'},
        ],
        'lifestyle': ['Identify and avoid triggers', 'Regular sleep schedule', 'Stress management', 'Adequate hydration', 'Limit caffeine']
    }
}


class MedicineEngine:
    """
    Evidence-based medicine recommendation system
    """

    def recommend(self, condition, symptoms=None):
        condition_lower = condition.lower()

        # Direct match
        for key in MEDICINE_DATABASE:
            if key in condition_lower or condition_lower in key:
                return self._format_recommendation(key, MEDICINE_DATABASE[key])

        # Symptom-based matching
        if symptoms:
            matched = self._match_by_symptoms(symptoms)
            if matched:
                return self._format_recommendation(matched, MEDICINE_DATABASE[matched])

        # Generic response
        return self._generic_recommendation(condition)

    def _match_by_symptoms(self, symptoms):
        symptom_map = {
            'chest pain': 'heart_disease',
            'palpitations': 'heart_disease',
            'high blood pressure': 'hypertension',
            'blood sugar': 'diabetes',
            'thirst': 'diabetes',
            'anxiety': 'anxiety',
            'panic': 'anxiety',
            'fever': 'fever',
            'headache': 'headache',
        }
        for symptom in symptoms:
            for key, condition in symptom_map.items():
                if key in symptom.lower():
                    return condition
        return None

    def _format_recommendation(self, condition_name, data):
        return {
            'condition': condition_name.replace('_', ' ').title(),
            'disclaimer': '⚠️ These recommendations are AI-generated for educational purposes only. Always consult a licensed physician before starting any medication.',
            'first_line_medications': data.get('first_line', []),
            'second_line_medications': data.get('second_line', []),
            'lifestyle_modifications': data.get('lifestyle', []),
            'monitoring_required': True,
            'follow_up': 'Schedule follow-up with physician in 4-6 weeks after starting treatment.'
        }

    def _generic_recommendation(self, condition):
        return {
            'condition': condition,
            'disclaimer': '⚠️ AI-generated guidance only. Consult a healthcare professional.',
            'first_line_medications': [],
            'second_line_medications': [],
            'lifestyle_modifications': [
                'Maintain a balanced diet rich in fruits and vegetables',
                'Regular physical activity (150 min/week)',
                'Adequate sleep (7-9 hours)',
                'Stress management techniques',
                'Regular medical checkups'
            ],
            'monitoring_required': True,
            'follow_up': 'Consult a physician for condition-specific medication guidance.'
        }
