from typing import Dict, Any, List
import re
from agents.base_agent import BaseAgent

class TranscriptionAgent(BaseAgent):
    """Agent responsible for processing and cleaning transcription text"""
    
    def __init__(self):
        super().__init__("TranscriptionAgent")
    
    def process(self, transcript_text: str) -> Dict[str, Any]:
        """
        Process the input transcript text
        
        Args:
            transcript_text: Raw transcript text
            
        Returns:
            Dict containing cleaned text and metadata
        """
        try:
            self.log_activity("Starting transcription processing")
            
            # Clean and process the transcript
            cleaned_text = self.clean_transcript(transcript_text)
            
            # Extract speaker information
            speakers = self.identify_speakers(cleaned_text)
            
            # Calculate basic metrics
            word_count = len(cleaned_text.split())
            confidence_score = self.calculate_transcription_confidence(cleaned_text)
            
            result = {
                "original_text": transcript_text,
                "cleaned_text": cleaned_text,
                "speakers": speakers,
                "word_count": word_count,
                "confidence_score": confidence_score,
                "processing_notes": self.get_processing_notes(transcript_text, cleaned_text)
            }
            
            self.log_activity("Transcription processing completed", {"word_count": word_count})
            
            return result
            
        except Exception as e:
            return self.handle_error(e, "transcription processing")
    
    def clean_transcript(self, text: str) -> str:
        """Clean and standardize the transcript text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Standardize speaker labels
        text = re.sub(r'Doctor\s*:', 'Doctor:', text, flags=re.IGNORECASE)
        text = re.sub(r'Patient\s*:', 'Patient:', text, flags=re.IGNORECASE)
        text = re.sub(r'Dr\.\s*\w+\s*:', 'Doctor:', text, flags=re.IGNORECASE)
        
        # Remove filler words and sounds
        fillers = [r'\buh\b', r'\bum\b', r'\ber\b', r'\blike\b(?=\s)', r'\byou know\b']
        for filler in fillers:
            text = re.sub(filler, '', text, flags=re.IGNORECASE)
        
        # Clean up punctuation
        text = re.sub(r'\s+([,.!?])', r'\1', text)
        text = re.sub(r'\.+', '.', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def identify_speakers(self, text: str) -> Dict[str, int]:
        """Identify and count speaker turns"""
        speaker_pattern = r'(Doctor|Patient):'
        speakers = re.findall(speaker_pattern, text, re.IGNORECASE)
        
        speaker_counts = {}
        for speaker in speakers:
            speaker_lower = speaker.lower().capitalize()
            speaker_counts[speaker_lower] = speaker_counts.get(speaker_lower, 0) + 1
        
        return speaker_counts
    
    def calculate_transcription_confidence(self, text: str) -> float:
        """Calculate confidence score based on text quality indicators"""
        confidence = 0.9  # Base confidence
        
        # Reduce confidence for very short text
        if len(text.split()) < 50:
            confidence -= 0.1
        
        # Reduce confidence for excessive repetition
        words = text.lower().split()
        unique_words = set(words)
        if len(words) > 0 and len(unique_words) / len(words) < 0.3:
            confidence -= 0.15
        
        # Reduce confidence for missing speaker labels
        if not re.search(r'(Doctor|Patient):', text, re.IGNORECASE):
            confidence -= 0.2
        
        # Ensure confidence is between 0 and 1
        return max(0.0, min(1.0, confidence))
    
    def get_processing_notes(self, original: str, cleaned: str) -> List[str]:
        """Generate notes about the processing performed"""
        notes = []
        
        if len(original) != len(cleaned):
            notes.append(f"Text length changed from {len(original)} to {len(cleaned)} characters")
        
        original_words = len(original.split())
        cleaned_words = len(cleaned.split())
        if original_words != cleaned_words:
            notes.append(f"Word count changed from {original_words} to {cleaned_words} words")
        
        if re.search(r'(Doctor|Patient):', cleaned, re.IGNORECASE):
            notes.append("Speaker labels detected and standardized")
        else:
            notes.append("Warning: No clear speaker labels detected")
        
        return notes
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback result for transcription errors"""
        return {
            "original_text": "",
            "cleaned_text": "Error processing transcript",
            "speakers": {},
            "word_count": 0,
            "confidence_score": 0.0,
            "processing_notes": ["Transcription processing failed"]
        }
