from typing import Dict, Any, List
import re
import json
from agents.base_agent import BaseAgent

class ConceptAgent(BaseAgent):
    """Agent responsible for extracting medical concepts from clinical text"""
    
    def __init__(self):
        super().__init__("ConceptAgent")
        self.medical_entities = self.load_medical_entities()
        self.confidence_threshold = 0.6
    
    def process(self, input_data) -> List[Dict[str, Any]]:
        """Process input data - alias for extract_concepts method"""
        return self.extract_concepts(input_data)
    
    def load_medical_entities(self) -> Dict[str, List[str]]:
        """Load medical entity patterns and vocabularies"""
        return {
            "medications": [
                r'\b(lisinopril|metformin|atorvastatin|amlodipine|simvastatin|metoprolol|losartan|hydrochlorothiazide|omeprazole|levothyroxine)\b',
                r'\b\w+\s*(mg|mcg|units?|tablets?|capsules?)\b',
                r'\b(take|taking|prescribed|medication|drug|pill)\s+\w+\b'
            ],
            "symptoms": [
                r'\b(pain|ache|headache|nausea|fatigue|dizziness|shortness of breath|chest pain|back pain)\b',
                r'\b(fever|cough|runny nose|sore throat|congestion|sneezing)\b',
                r'\b(anxiety|depression|stress|insomnia|mood)\b'
            ],
            "conditions": [
                r'\b(hypertension|diabetes|depression|anxiety|asthma|copd|heart disease|stroke)\b',
                r'\b(high blood pressure|low blood pressure|blood sugar|cholesterol)\b',
                r'\b(arthritis|osteoporosis|cancer|infection|allergies)\b'
            ],
            "vitals": [
                r'\b\d+/\d+\b',  # Blood pressure
                r'\b\d+\s*(bpm|beats per minute)\b',  # Heart rate
                r'\b\d+\.?\d*\s*°?[CF]\b',  # Temperature
                r'\b\d+\.?\d*\s*(lbs?|kg|pounds?|kilograms?)\b',  # Weight
                r'\b(blood pressure|heart rate|temperature|weight|height|bmi)\b'
            ],
            "procedures": [
                r'\b(blood test|x-ray|mri|ct scan|ultrasound|ekg|ecg|colonoscopy|mammogram)\b',
                r'\b(examination|exam|checkup|physical|inspection|palpation|auscultation)\b'
            ],
            "body_parts": [
                r'\b(head|neck|chest|abdomen|back|arm|leg|heart|lung|liver|kidney|brain)\b',
                r'\b(eyes|ears|nose|throat|mouth|skin|joints|muscles|bones)\b'
            ],
            "temporal": [
                r'\b(today|yesterday|last week|last month|last year|ago|since|for)\b',
                r'\b(\d+\s*(days?|weeks?|months?|years?)\s*(ago|since))\b',
                r'\b(morning|afternoon|evening|night|daily|weekly|monthly)\b'
            ]
        }
    
    def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract medical concepts from the clinical text
        
        Args:
            text: Clinical text to analyze
            
        Returns:
            List of extracted medical concepts with metadata
        """
        try:
            self.log_activity("Starting concept extraction")
            
            concepts = []
            text_lower = text.lower()
            
            # Extract concepts by category
            for category, patterns in self.medical_entities.items():
                category_concepts = self.extract_category_concepts(text, text_lower, category, patterns)
                concepts.extend(category_concepts)
            
            # Extract medication dosages and frequencies
            medication_details = self.extract_medication_details(text)
            concepts.extend(medication_details)
            
            # Extract vital sign measurements
            vital_measurements = self.extract_vital_measurements(text)
            concepts.extend(vital_measurements)
            
            # Remove duplicates and rank by confidence
            concepts = self.deduplicate_and_rank(concepts)
            
            # Add contextual information
            concepts = self.add_context_information(concepts, text)
            
            self.log_activity("Concept extraction completed", {"concepts_found": len(concepts)})
            
            return concepts
            
        except Exception as e:
            return self.handle_error(e, "concept extraction")
    
    def extract_category_concepts(self, text: str, text_lower: str, category: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Extract concepts for a specific medical category"""
        concepts = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            
            for match in matches:
                concept_text = match.group(0)
                start_pos = match.start()
                end_pos = match.end()
                
                # Get surrounding context
                context_start = max(0, start_pos - 50)
                context_end = min(len(text), end_pos + 50)
                context = text[context_start:context_end]
                
                # Calculate confidence based on context and pattern specificity
                confidence = self.calculate_concept_confidence(concept_text, context, category)
                
                if confidence >= self.confidence_threshold:
                    concepts.append({
                        "text": concept_text,
                        "category": category,
                        "confidence": confidence,
                        "start_position": start_pos,
                        "end_position": end_pos,
                        "context": context.strip(),
                        "pattern_matched": pattern
                    })
        
        return concepts
    
    def extract_medication_details(self, text: str) -> List[Dict[str, Any]]:
        """Extract detailed medication information including dosages and frequencies"""
        medication_concepts = []
        
        # Pattern for medication with dosage
        med_pattern = r'\b(\w+)\s+(\d+\.?\d*)\s*(mg|mcg|units?|tablets?)\b'
        matches = re.finditer(med_pattern, text, re.IGNORECASE)
        
        for match in matches:
            medication = match.group(1)
            dosage = match.group(2)
            unit = match.group(3)
            
            # Look for frequency information nearby
            context_start = max(0, match.start() - 100)
            context_end = min(len(text), match.end() + 100)
            context = text[context_start:context_end]
            
            frequency = self.extract_frequency(context)
            
            medication_concepts.append({
                "text": match.group(0),
                "category": "medication_detailed",
                "medication_name": medication,
                "dosage": dosage,
                "unit": unit,
                "frequency": frequency,
                "confidence": 0.9,
                "start_position": match.start(),
                "end_position": match.end(),
                "context": context.strip()
            })
        
        return medication_concepts
    
    def extract_vital_measurements(self, text: str) -> List[Dict[str, Any]]:
        """Extract specific vital sign measurements"""
        vital_concepts = []
        
        # Blood pressure pattern
        bp_pattern = r'\b(\d{2,3})\s*/\s*(\d{2,3})\b'
        bp_matches = re.finditer(bp_pattern, text)
        
        for match in bp_matches:
            systolic = int(match.group(1))
            diastolic = int(match.group(2))
            
            # Validate blood pressure ranges
            if 80 <= systolic <= 250 and 40 <= diastolic <= 150:
                vital_concepts.append({
                    "text": match.group(0),
                    "category": "vital_measurement",
                    "vital_type": "blood_pressure",
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "confidence": 0.95,
                    "start_position": match.start(),
                    "end_position": match.end(),
                    "interpretation": self.interpret_blood_pressure(systolic, diastolic)
                })
        
        # Heart rate pattern
        hr_pattern = r'\b(\d{2,3})\s*(bpm|beats per minute)\b'
        hr_matches = re.finditer(hr_pattern, text, re.IGNORECASE)
        
        for match in hr_matches:
            heart_rate = int(match.group(1))
            
            if 30 <= heart_rate <= 200:  # Reasonable heart rate range
                vital_concepts.append({
                    "text": match.group(0),
                    "category": "vital_measurement",
                    "vital_type": "heart_rate",
                    "value": heart_rate,
                    "unit": "bpm",
                    "confidence": 0.9,
                    "start_position": match.start(),
                    "end_position": match.end(),
                    "interpretation": self.interpret_heart_rate(heart_rate)
                })
        
        return vital_concepts
    
    def extract_frequency(self, context: str) -> str:
        """Extract medication frequency from context"""
        frequency_patterns = [
            (r'\b(once|one time)\s*(a\s*day|daily|per day)\b', 'once daily'),
            (r'\b(twice|two times?)\s*(a\s*day|daily|per day)\b', 'twice daily'),
            (r'\b(three times?)\s*(a\s*day|daily|per day)\b', 'three times daily'),
            (r'\bevery\s*(\d+)\s*hours?\b', 'every {} hours'),
            (r'\bas\s*needed\b', 'as needed'),
            (r'\bwith\s*(meals?|food)\b', 'with meals')
        ]
        
        context_lower = context.lower()
        for pattern, frequency in frequency_patterns:
            match = re.search(pattern, context_lower)
            if match:
                if '{}' in frequency:
                    return frequency.format(match.group(1))
                return frequency
        
        return "frequency not specified"
    
    def calculate_concept_confidence(self, concept_text: str, context: str, category: str) -> float:
        """Calculate confidence score for an extracted concept"""
        confidence = 0.7  # Base confidence
        
        # Boost confidence for specific categories
        if category in ["medications", "conditions", "vitals"]:
            confidence += 0.1
        
        # Boost confidence for longer, more specific terms
        if len(concept_text) > 5:
            confidence += 0.05
        
        # Boost confidence for medical context keywords
        medical_context_words = ["patient", "doctor", "medication", "diagnosis", "treatment", "symptoms"]
        context_lower = context.lower()
        for word in medical_context_words:
            if word in context_lower:
                confidence += 0.02
        
        # Reduce confidence for very short or common words
        if len(concept_text) <= 3 or concept_text.lower() in ["the", "and", "for", "with"]:
            confidence -= 0.3
        
        return min(1.0, max(0.0, confidence))
    
    def interpret_blood_pressure(self, systolic: int, diastolic: int) -> str:
        """Interpret blood pressure readings"""
        if systolic < 120 and diastolic < 80:
            return "normal"
        elif systolic < 130 and diastolic < 80:
            return "elevated"
        elif systolic < 140 or diastolic < 90:
            return "stage_1_hypertension"
        elif systolic < 180 or diastolic < 120:
            return "stage_2_hypertension"
        else:
            return "hypertensive_crisis"
    
    def interpret_heart_rate(self, heart_rate: int) -> str:
        """Interpret heart rate readings"""
        if heart_rate < 60:
            return "bradycardia"
        elif heart_rate <= 100:
            return "normal"
        else:
            return "tachycardia"
    
    def deduplicate_and_rank(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicates and rank concepts by confidence"""
        # Group similar concepts
        unique_concepts = []
        seen_texts = set()
        
        # Sort by confidence first
        concepts.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        for concept in concepts:
            concept_text = concept["text"].lower().strip()
            
            # Skip if we've seen this exact text
            if concept_text in seen_texts:
                continue
            
            seen_texts.add(concept_text)
            unique_concepts.append(concept)
        
        return unique_concepts
    
    def add_context_information(self, concepts: List[Dict[str, Any]], full_text: str) -> List[Dict[str, Any]]:
        """Add additional context information to concepts"""
        for concept in concepts:
            # Add negation detection
            concept["is_negated"] = self.detect_negation(concept["context"])
            
            # Add temporal context
            concept["temporal_context"] = self.extract_temporal_context(concept["context"])
            
            # Add speaker attribution if available
            concept["attributed_to"] = self.determine_speaker(concept, full_text)
        
        return concepts
    
    def detect_negation(self, context: str) -> bool:
        """Detect if a concept is negated in context"""
        negation_words = ["no", "not", "never", "without", "denies", "negative", "absence of"]
        context_lower = context.lower()
        
        for neg_word in negation_words:
            if neg_word in context_lower:
                return True
        
        return False
    
    def extract_temporal_context(self, context: str) -> str:
        """Extract temporal information from context"""
        temporal_patterns = [
            r'\b(today|yesterday|last week|last month|last year)\b',
            r'\b(\d+\s*(days?|weeks?|months?|years?)\s*ago)\b',
            r'\b(currently|now|recently|previously)\b'
        ]
        
        context_lower = context.lower()
        for pattern in temporal_patterns:
            match = re.search(pattern, context_lower)
            if match:
                return match.group(0)
        
        return "temporal context not specified"
    
    def determine_speaker(self, concept: Dict[str, Any], full_text: str) -> str:
        """Determine which speaker mentioned the concept"""
        concept_position = concept.get("start_position", 0)
        
        # Find the most recent speaker label before this position
        speaker_pattern = r'(Doctor|Patient):'
        speakers = list(re.finditer(speaker_pattern, full_text, re.IGNORECASE))
        
        current_speaker = "unknown"
        for match in speakers:
            if match.start() <= concept_position:
                current_speaker = match.group(1).lower()
            else:
                break
        
        return current_speaker
    
    def get_fallback_result(self) -> List[Dict[str, Any]]:
        """Provide fallback result when concept extraction fails"""
        return [
            {
                "text": "concept extraction failed",
                "category": "error",
                "confidence": 0.0,
                "error": "Unable to process medical concepts due to technical error"
            }
        ]
