from typing import Dict, Any, List
import re
from agents.base_agent import BaseAgent

class ContextAgent(BaseAgent):
    """Agent responsible for analyzing context and segmenting transcript into SOAP sections"""
    
    def __init__(self):
        super().__init__("ContextAgent")
        self.soap_keywords = {
            "subjective": [
                "how are you feeling", "symptoms", "pain", "complain", "history",
                "tell me about", "describe", "when did", "how long", "patient reports",
                "chief complaint", "feels", "experiencing"
            ],
            "objective": [
                "blood pressure", "temperature", "heart rate", "examination", "vital signs",
                "looks", "appears", "physical exam", "inspection", "palpation",
                "auscultation", "percussion", "labs", "test results", "measurements"
            ],
            "assessment": [
                "diagnosis", "impression", "assessment", "condition", "likely",
                "differential", "ruled out", "consistent with", "suggests",
                "indicates", "conclude", "findings suggest"
            ],
            "plan": [
                "treatment", "plan", "prescribe", "medication", "follow up",
                "return", "schedule", "continue", "start", "stop", "increase",
                "decrease", "refer", "recommend", "instructions"
            ]
        }
    
    def process(self, input_data) -> Dict[str, Any]:
        """Process input data - alias for analyze method"""
        return self.analyze(input_data)
    
    def analyze(self, transcript: str) -> Dict[str, Any]:
        """
        Analyze the transcript and identify SOAP sections
        
        Args:
            transcript: Cleaned transcript text
            
        Returns:
            Dict containing analysis results and SOAP segments
        """
        try:
            self.log_activity("Starting context analysis")
            
            # Segment the transcript
            segments = self.segment_transcript(transcript)
            
            # Classify each segment
            classified_segments = self.classify_segments(segments)
            
            # Extract clinical context
            clinical_context = self.extract_clinical_context(transcript)
            
            # Identify conversation flow
            conversation_flow = self.analyze_conversation_flow(segments)
            
            result = {
                "segments": classified_segments,
                "clinical_context": clinical_context,
                "conversation_flow": conversation_flow,
                "soap_mapping": self.map_to_soap_sections(classified_segments),
                "confidence_score": self.calculate_classification_confidence(classified_segments)
            }
            
            self.log_activity("Context analysis completed", {
                "segments_count": len(segments),
                "soap_sections_identified": len(result["soap_mapping"])
            })
            
            return result
            
        except Exception as e:
            return self.handle_error(e, "context analysis")
    
    def segment_transcript(self, transcript: str) -> List[Dict[str, Any]]:
        """Segment transcript into speaker turns and exchanges"""
        segments = []
        
        # Split by speaker changes
        parts = re.split(r'(Doctor:|Patient:)', transcript, flags=re.IGNORECASE)
        
        current_speaker = None
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
                
            if part.lower() in ['doctor:', 'patient:']:
                current_speaker = part.replace(':', '').lower().capitalize()
            elif current_speaker:
                segments.append({
                    "speaker": current_speaker,
                    "text": part,
                    "order": len(segments),
                    "word_count": len(part.split())
                })
        
        return segments
    
    def classify_segments(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Classify each segment into potential SOAP categories"""
        classified = []
        
        for segment in segments:
            text = segment["text"].lower()
            soap_scores = {}
            
            # Calculate scores for each SOAP section
            for section, keywords in self.soap_keywords.items():
                score = 0
                for keyword in keywords:
                    if keyword in text:
                        score += 1
                soap_scores[section] = score / len(keywords)  # Normalize
            
            # Determine primary classification
            primary_classification = max(soap_scores, key=soap_scores.get) if soap_scores else "general"
            confidence = max(soap_scores.values()) if soap_scores else 0.1
            
            classified_segment = {
                **segment,
                "primary_classification": primary_classification,
                "classification_confidence": confidence,
                "soap_scores": soap_scores,
                "keywords_found": self.find_keywords_in_text(text)
            }
            classified.append(classified_segment)
        
        return classified
    
    def extract_clinical_context(self, transcript: str) -> Dict[str, Any]:
        """Extract clinical context information"""
        context = {
            "visit_type": self.identify_visit_type(transcript),
            "urgency_level": self.assess_urgency(transcript),
            "patient_concerns": self.extract_patient_concerns(transcript),
            "clinical_indicators": self.identify_clinical_indicators(transcript)
        }
        return context
    
    def identify_visit_type(self, transcript: str) -> str:
        """Identify the type of clinical visit"""
        text = transcript.lower()
        
        if any(word in text for word in ["follow up", "follow-up", "return visit", "check up"]):
            return "follow_up"
        elif any(word in text for word in ["new patient", "first time", "initial"]):
            return "new_patient"
        elif any(word in text for word in ["urgent", "emergency", "pain", "severe"]):
            return "urgent_care"
        elif any(word in text for word in ["annual", "physical", "routine", "checkup"]):
            return "routine_physical"
        else:
            return "standard_visit"
    
    def assess_urgency(self, transcript: str) -> str:
        """Assess the urgency level of the visit"""
        text = transcript.lower()
        
        urgent_indicators = ["severe", "emergency", "urgent", "immediately", "chest pain", "difficulty breathing"]
        moderate_indicators = ["pain", "discomfort", "concerning", "worried"]
        
        if any(indicator in text for indicator in urgent_indicators):
            return "high"
        elif any(indicator in text for indicator in moderate_indicators):
            return "moderate"
        else:
            return "low"
    
    def extract_patient_concerns(self, transcript: str) -> List[str]:
        """Extract main patient concerns from the conversation"""
        concerns = []
        
        # Look for patient statements about symptoms or problems
        patient_sections = re.findall(r'Patient:(.*?)(?=Doctor:|$)', transcript, re.IGNORECASE | re.DOTALL)
        
        concern_patterns = [
            r'(i\'ve been having|experiencing|feeling|my \w+ (is|has been))',
            r'(pain|ache|hurt|discomfort)',
            r'(worried about|concerned about|problem with)'
        ]
        
        for section in patient_sections:
            for pattern in concern_patterns:
                matches = re.findall(pattern, section.lower())
                if matches:
                    # Extract surrounding context
                    sentences = section.split('.')
                    for sentence in sentences:
                        if any(re.search(pattern, sentence.lower()) for pattern in concern_patterns):
                            concerns.append(sentence.strip())
        
        return list(set(concerns))  # Remove duplicates
    
    def identify_clinical_indicators(self, transcript: str) -> List[str]:
        """Identify clinical indicators mentioned in the conversation"""
        indicators = []
        
        # Medical terms and measurements
        medical_patterns = [
            r'\b\d+/\d+\b',  # Blood pressure
            r'\b\d+\s*(mg|mcg|units?)\b',  # Medications
            r'\b(blood pressure|heart rate|temperature|weight)\b',
            r'\b(hypertension|diabetes|depression|anxiety)\b'
        ]
        
        for pattern in medical_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            indicators.extend(matches)
        
        return indicators
    
    def analyze_conversation_flow(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the flow and structure of the conversation"""
        doctor_segments = [s for s in segments if s["speaker"] == "Doctor"]
        patient_segments = [s for s in segments if s["speaker"] == "Patient"]
        
        return {
            "total_exchanges": len(segments),
            "doctor_turns": len(doctor_segments),
            "patient_turns": len(patient_segments),
            "average_doctor_response_length": sum(s["word_count"] for s in doctor_segments) / len(doctor_segments) if doctor_segments else 0,
            "average_patient_response_length": sum(s["word_count"] for s in patient_segments) / len(patient_segments) if patient_segments else 0,
            "conversation_balance": len(patient_segments) / len(doctor_segments) if doctor_segments else 0
        }
    
    def map_to_soap_sections(self, classified_segments: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Map classified segments to SOAP sections"""
        soap_mapping = {
            "subjective": [],
            "objective": [],
            "assessment": [],
            "plan": []
        }
        
        for segment in classified_segments:
            primary = segment["primary_classification"]
            if primary in soap_mapping:
                soap_mapping[primary].append(segment)
            else:
                # Default to subjective for unclear segments from patients
                if segment["speaker"] == "Patient":
                    soap_mapping["subjective"].append(segment)
                else:
                    soap_mapping["assessment"].append(segment)
        
        return soap_mapping
    
    def calculate_classification_confidence(self, segments: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the classification"""
        if not segments:
            return 0.0
        
        confidences = [s["classification_confidence"] for s in segments]
        return sum(confidences) / len(confidences)
    
    def find_keywords_in_text(self, text: str) -> Dict[str, List[str]]:
        """Find SOAP keywords present in the text"""
        found_keywords = {}
        
        for section, keywords in self.soap_keywords.items():
            found_in_section = []
            for keyword in keywords:
                if keyword in text:
                    found_in_section.append(keyword)
            if found_in_section:
                found_keywords[section] = found_in_section
        
        return found_keywords
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback result for context analysis errors"""
        return {
            "segments": [],
            "clinical_context": {
                "visit_type": "unknown",
                "urgency_level": "low",
                "patient_concerns": [],
                "clinical_indicators": []
            },
            "conversation_flow": {},
            "soap_mapping": {"subjective": [], "objective": [], "assessment": [], "plan": []},
            "confidence_score": 0.0
        }
