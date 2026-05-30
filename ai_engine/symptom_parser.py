"""
AURA MEDIX — Symptom Analysis Engine
NLP-based symptom parsing and disease suggestion
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

class SymptomAnalyzer:
    """Advanced NLP symptom analysis and disease mapping"""
    
    def __init__(self):
        self.symptom_disease_mapping = {
            'fever': ['flu', 'covid19', 'pneumonia', 'malaria', 'typhoid'],
            'cough': ['covid19', 'pneumonia', 'bronchitis', 'asthma', 'tuberculosis'],
            'headache': ['migraine', 'tension_headache', 'meningitis', 'covid19'],
            'chest pain': ['heart_disease', 'angina', 'pneumonia', 'anxiety'],
            'shortness of breath': ['asthma', 'pneumonia', 'heart_disease', 'covid19', 'anxiety'],
            'nausea': ['gastroenteritis', 'food_poisoning', 'pregnancy', 'migraines'],
            'vomiting': ['gastroenteritis', 'food_poisoning', 'appendicitis', 'migraines'],
            'diarrhea': ['gastroenteritis', 'food_poisoning', 'ibs', 'cholera'],
            'fatigue': ['anemia', 'depression', 'thyroid_disease', 'diabetes', 'covid19'],
            'joint pain': ['arthritis', 'rheumatism', 'lupus', 'lyme_disease'],
            'muscle pain': ['influenza', 'covid19', 'fibromyalgia', 'lyme_disease'],
            'sore throat': ['pharyngitis', 'tonsillitis', 'covid19', 'strep_infection'],
            'rash': ['measles', 'chickenpox', 'dermatitis', 'allergies', 'lyme_disease'],
            'dizziness': ['vertigo', 'anemia', 'low_blood_pressure', 'ear_infection'],
            'difficulty breathing': ['asthma', 'pneumonia', 'pulmonary_embolism', 'anxiety'],
        }
        
        self.severity_keywords = {
            'critical': ['severe', 'critical', 'emergency', 'unconscious', 'unable to move'],
            'high': ['severe', 'intense', 'unbearable', 'constant', 'worsening'],
            'medium': ['moderate', 'significant', 'persistent', 'frequent'],
            'low': ['mild', 'slight', 'occasional', 'manageable']
        }
    
    def analyze_symptoms(self, symptoms_text):
        """
        Analyze symptom description and suggest possible diseases
        
        Args:
            symptoms_text: User description of symptoms
        
        Returns:
            Dictionary with analysis results
        """
        symptoms_text = symptoms_text.lower()
        
        # Extract mentioned symptoms
        mentioned_symptoms = self._extract_symptoms(symptoms_text)
        
        # Assess severity
        severity = self._assess_severity(symptoms_text)
        
        # Get disease suggestions
        disease_scores = self._get_disease_suggestions(mentioned_symptoms)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(mentioned_symptoms, severity)
        
        return {
            'mentioned_symptoms': mentioned_symptoms,
            'severity': severity,
            'possible_diseases': disease_scores,
            'recommendations': recommendations,
            'requires_immediate_care': severity == 'critical'
        }
    
    def _extract_symptoms(self, text):
        """Extract mentioned symptoms from text"""
        mentioned = []
        for symptom in self.symptom_disease_mapping.keys():
            if symptom.lower() in text:
                mentioned.append(symptom)
        
        # If no specific symptoms found, return generic list
        if not mentioned:
            mentioned = ['general_malaise']
        
        return mentioned
    
    def _assess_severity(self, text):
        """Assess severity level based on keywords"""
        text_lower = text.lower()
        
        for severity, keywords in self.severity_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return severity
        
        return 'medium'
    
    def _get_disease_suggestions(self, symptoms):
        """Get disease suggestions based on mentioned symptoms"""
        disease_count = {}
        
        for symptom in symptoms:
            diseases = self.symptom_disease_mapping.get(symptom, [])
            for disease in diseases:
                disease_count[disease] = disease_count.get(disease, 0) + 1
        
        # Calculate confidence scores
        total_symptoms = len(symptoms)
        disease_scores = []
        
        for disease, count in disease_count.items():
            confidence = (count / total_symptoms) * 100
            disease_scores.append({
                'disease': disease.replace('_', ' ').title(),
                'confidence': min(100, confidence),
                'matching_symptoms': count
            })
        
        # Sort by confidence
        disease_scores.sort(key=lambda x: x['confidence'], reverse=True)
        
        return disease_scores[:5]  # Top 5 suggestions
    
    def _generate_recommendations(self, symptoms, severity):
        """Generate recommendations based on symptoms and severity"""
        recommendations = []
        
        if severity == 'critical':
            recommendations.append('🚨 URGENT: Seek immediate emergency medical care (Call 911 or local emergency)')
            recommendations.append('Do not wait for appointment')
            recommendations.append('Visit nearest emergency room')
        
        elif severity == 'high':
            recommendations.append('⚠️ Contact healthcare provider immediately')
            recommendations.append('Request urgent appointment within 24 hours')
            recommendations.append('Monitor symptoms closely')
        
        else:
            recommendations.append('📋 Schedule appointment with healthcare provider')
            recommendations.append('Keep symptom diary with timeline')
            recommendations.append('Monitor for worsening symptoms')
        
        # Add symptom-specific recommendations
        if 'chest pain' in symptoms or 'difficulty breathing' in symptoms:
            recommendations.append('🫀 For chest pain/breathing: Cardiac assessment recommended')
        
        if 'fever' in symptoms:
            recommendations.append('🌡️ For fever: Monitor temperature, stay hydrated')
        
        if 'severe headache' in symptoms:
            recommendations.append('🤕 For severe headache: Rest in dark, quiet room; consider neurological evaluation')
        
        recommendations.append('Stay hydrated and get adequate rest')
        recommendations.append('Avoid self-medication without professional advice')
        
        return recommendations

# Create singleton instance
analyzer = SymptomAnalyzer()
