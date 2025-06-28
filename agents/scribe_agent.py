from typing import Dict, Any, List
import os
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

# Load environment variables
load_dotenv()

class ScribeAgent(BaseAgent):
    """Agent responsible for generating SOAP notes from clinical conversations"""
    
    def __init__(self):
        super().__init__("ScribeAgent")
        self.llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.model_name = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.initialize_llm()
    
    def process(self, input_data) -> Dict[str, Any]:
        """Process input data - expects tuple of (transcript, segments)"""
        if isinstance(input_data, tuple) and len(input_data) == 2:
            transcript, segments = input_data
            return self.generate_soap_notes(transcript, segments)
        else:
            # Fallback for single transcript
            return self.generate_soap_notes(input_data, [])
    
    def initialize_llm(self):
        """Initialize the LLM based on the configured provider"""
        try:
            if self.llm_provider == "openai":
                import openai
                self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            elif self.llm_provider == "google":
                import google.generativeai as genai
                genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                self.client = genai.GenerativeModel(self.model_name)
            elif self.llm_provider == "anthropic":
                import anthropic
                self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        except Exception as e:
            self.logger.warning(f"Failed to initialize LLM: {e}. Using fallback mode.")
            self.client = None
    
    def generate_soap_notes(self, transcript: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Generate SOAP notes from the clinical transcript
        
        Args:
            transcript: The cleaned transcript text
            segments: Segmented and classified conversation parts
            
        Returns:
            Dict containing SOAP sections
        """
        try:
            self.log_activity("Starting SOAP note generation")
            
            if self.client is None:
                # Fallback to rule-based generation
                return self.generate_soap_fallback(transcript, segments)
            
            # Generate each SOAP section using LLM
            soap_notes = {}
            
            for section in ["subjective", "objective", "assessment", "plan"]:
                soap_notes[section] = self.generate_soap_section(
                    section, transcript, segments
                )
            
            # Post-process and validate
            soap_notes = self.post_process_soap_notes(soap_notes)
            
            self.log_activity("SOAP note generation completed")
            
            return soap_notes
            
        except Exception as e:
            return self.handle_error(e, "SOAP note generation")
    
    def generate_soap_section(self, section: str, transcript: str, segments: List[Dict[str, Any]]) -> str:
        """Generate a specific SOAP section using LLM"""
        
        # Filter relevant segments for this section
        relevant_segments = [s for s in segments if s.get("primary_classification") == section]
        
        # Create section-specific prompt
        prompt = self.create_soap_prompt(section, transcript, relevant_segments)
        
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == "google":
                response = self.client.generate_content(
                    f"{self.get_system_prompt()}\n\n{prompt}",
                    generation_config={
                        "max_output_tokens": 500,
                        "temperature": 0.3
                    }
                )
                return response.text.strip()
            
            elif self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,
                    temperature=0.3,
                    system=self.get_system_prompt(),
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()
        
        except Exception as e:
            self.logger.error(f"LLM generation failed for {section}: {e}")
            return self.generate_section_fallback(section, transcript, relevant_segments)
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for SOAP note generation"""
        return """You are an expert medical scribe AI assistant specializing in generating accurate, concise SOAP notes from clinical encounters.

Your task is to extract and organize clinical information into the appropriate SOAP section format:

SUBJECTIVE: Patient's reported symptoms, concerns, history, and subjective experiences
OBJECTIVE: Observable findings, vital signs, physical examination results, test results
ASSESSMENT: Clinical impressions, diagnoses, differential diagnoses
PLAN: Treatment plans, medications, follow-up instructions, referrals

Guidelines:
- Use professional medical terminology
- Be concise but comprehensive
- Include specific details (medications, dosages, vital signs, timelines)
- Maintain patient privacy (use generic identifiers)
- Focus only on medically relevant information
- Use bullet points or short paragraphs for clarity
- If information is unclear or missing, note it appropriately"""
    
    def create_soap_prompt(self, section: str, transcript: str, relevant_segments: List[Dict[str, Any]]) -> str:
        """Create a section-specific prompt for SOAP generation"""
        
        section_instructions = {
            "subjective": "Extract and summarize what the patient reports about their symptoms, concerns, medical history, and subjective experiences. Include chief complaint, history of present illness, and patient-reported information.",
            
            "objective": "Extract and summarize observable findings mentioned in the conversation including vital signs, physical examination findings, test results, and any objective measurements or observations made by the clinician.",
            
            "assessment": "Summarize the clinician's assessment, clinical impressions, working diagnoses, and any differential diagnoses discussed. Include the healthcare provider's clinical reasoning and conclusions.",
            
            "plan": "Extract and organize the treatment plan including medications (with dosages), follow-up instructions, lifestyle recommendations, referrals, and any other planned interventions or monitoring."
        }
        
        prompt = f"""Generate the {section.upper()} section of a SOAP note based on the following clinical conversation.

Instructions: {section_instructions[section]}

Clinical Conversation:
{transcript}

Please provide only the {section.upper()} section content, formatted professionally:"""
        
        if relevant_segments:
            prompt += f"\n\nRelevant conversation segments for {section}:\n"
            for segment in relevant_segments[:3]:  # Limit to top 3 most relevant
                prompt += f"- {segment['speaker']}: {segment['text'][:200]}...\n"
        
        return prompt
    
    def generate_soap_fallback(self, transcript: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate SOAP notes using rule-based approach when LLM is unavailable"""
        
        soap_notes = {
            "subjective": "Patient reports concerns as documented in the conversation. ",
            "objective": "Clinical findings and measurements as observed. ",
            "assessment": "Clinical assessment based on presented information. ",
            "plan": "Treatment and follow-up plan as discussed. "
        }
        
        # Extract information from segments
        for segment in segments:
            text = segment["text"]
            speaker = segment["speaker"]
            classification = segment.get("primary_classification", "general")
            
            if speaker == "Patient" and classification in ["subjective", "general"]:
                soap_notes["subjective"] += f"{text[:100]}... "
            elif speaker == "Doctor":
                if "blood pressure" in text.lower() or "vital" in text.lower():
                    soap_notes["objective"] += f"{text[:100]}... "
                elif any(word in text.lower() for word in ["diagnosis", "assessment", "think", "likely"]):
                    soap_notes["assessment"] += f"{text[:100]}... "
                elif any(word in text.lower() for word in ["prescribe", "continue", "follow up", "recommend"]):
                    soap_notes["plan"] += f"{text[:100]}... "
        
        return soap_notes
    
    def generate_section_fallback(self, section: str, transcript: str, segments: List[Dict[str, Any]]) -> str:
        """Generate improved fallback content for a specific SOAP section using transcript and segments."""
        if not segments:
            return "No information available."
        if section == "subjective":
            complaints = [s["text"] for s in segments if s.get("speaker", "").lower() == "patient"]
            if complaints:
                return "Patient reports: " + "; ".join(complaints)
            return "Patient's subjective complaints as described in the encounter."
        elif section == "objective":
            findings = [s["text"] for s in segments if s.get("speaker", "").lower() == "doctor" and any(word in s["text"].lower() for word in ["blood pressure", "exam", "findings", "vital", "measurement"])]
            if findings:
                return "Exam findings: " + "; ".join(findings)
            return "Physical examination findings and vital signs as documented during the encounter."
        elif section == "assessment":
            # Try to infer assessment from doctor's statements
            assessments = [s["text"] for s in segments if s.get("speaker", "").lower() == "doctor" and any(word in s["text"].lower() for word in ["diagnosis", "impression", "likely", "assessment", "condition"])]
            if assessments:
                return "Assessment: " + "; ".join(assessments)
            return "Clinical assessment and diagnostic impressions based on the presented information."
        elif section == "plan":
            plans = [s["text"] for s in segments if s.get("speaker", "").lower() == "doctor" and any(word in s["text"].lower() for word in ["plan", "prescribe", "medication", "follow up", "return", "schedule", "continue", "start", "stop", "increase", "decrease", "refer", "recommend", "instructions"])]
            if plans:
                return "Plan: " + "; ".join(plans)
            return "Treatment plan and follow-up instructions as discussed with the patient."
        return "Information not available for this section."
    
    def post_process_soap_notes(self, soap_notes: Dict[str, str]) -> Dict[str, str]:
        """Post-process and validate the generated SOAP notes"""
        
        processed_notes = {}
        
        for section, content in soap_notes.items():
            # Clean up the content
            content = content.strip()
            
            # Ensure minimum content length
            if len(content) < 10:
                content = self.generate_section_fallback(section, "", [])
            
            # Format consistently
            if not content.endswith('.'):
                content += '.'
            
            # Capitalize first letter
            if content and content[0].islower():
                content = content[0].upper() + content[1:]
            
            processed_notes[section] = content
        
        return processed_notes
    
    def validate_soap_completeness(self, soap_notes: Dict[str, str]) -> Dict[str, Any]:
        """Validate the completeness and quality of generated SOAP notes"""
        
        validation_results = {
            "is_complete": True,
            "missing_sections": [],
            "quality_score": 0.0,
            "recommendations": []
        }
        
        required_sections = ["subjective", "objective", "assessment", "plan"]
        
        for section in required_sections:
            if section not in soap_notes or len(soap_notes[section].strip()) < 10:
                validation_results["missing_sections"].append(section)
                validation_results["is_complete"] = False
        
        # Calculate quality score
        total_length = sum(len(content) for content in soap_notes.values())
        if total_length > 200:
            validation_results["quality_score"] = min(1.0, total_length / 500)
        else:
            validation_results["quality_score"] = 0.3
        
        # Add recommendations
        if validation_results["missing_sections"]:
            validation_results["recommendations"].append(
                f"Consider adding content to: {', '.join(validation_results['missing_sections'])}"
            )
        
        return validation_results
    
    def get_fallback_result(self) -> Dict[str, str]:
        """Provide fallback SOAP notes when generation fails"""
        return {
            "subjective": "Unable to process patient-reported information due to technical error.",
            "objective": "Unable to process objective findings due to technical error.",
            "assessment": "Unable to process clinical assessment due to technical error.", 
            "plan": "Unable to process treatment plan due to technical error."
        }
