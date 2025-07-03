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
        self.client = None  # Initialize client to None first
        try:
            if self.llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY not found in environment variables")
                    return
                    
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                self.logger.info("OpenAI client initialized successfully")
                
            elif self.llm_provider == "google":
                api_key = os.getenv("GOOGLE_API_KEY") 
                if not api_key:
                    self.logger.warning("GOOGLE_API_KEY not found in environment variables")
                    return
                    
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.model_name)
                self.logger.info("Google client initialized successfully")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize LLM client: {e}. Using fallback mode.")
            self.client = None
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback SOAP notes when processing fails"""
        return {
            "subjective": "Unable to process patient-reported information due to technical error.",
            "objective": "Unable to process objective findings due to technical error.", 
            "assessment": "Unable to process clinical assessment due to technical error.",
            "plan": "Unable to process treatment plan due to technical error."
        }

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
            
            # Check if client exists and is properly initialized
            if not hasattr(self, 'client') or self.client is None:
                # Fallback to rule-based generation
                self.logger.warning("LLM client not available, using fallback generation")
                return self.generate_soap_fallback(transcript, segments)
            
            # Generate all SOAP sections in a single LLM call for better performance
            soap_notes = self.generate_complete_soap_notes(transcript, segments)
            
            # Post-process and validate
            soap_notes = self.post_process_soap_notes(soap_notes)
            
            self.log_activity("SOAP note generation completed")
            
            return soap_notes
            
        except Exception as e:
            self.logger.error(f"Error in SOAP generation: {e}")
            # Return fallback SOAP notes directly instead of error dict
            return self.generate_soap_fallback(transcript, segments)
    
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
    
    def generate_complete_soap_notes(self, transcript: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate all SOAP sections in a single LLM call for better performance"""
        
        # Create comprehensive prompt for all sections
        prompt = self.create_complete_soap_prompt(transcript, segments)
        
        try:
            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.get_system_prompt()},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1500,  # Increased for all sections
                    temperature=0.3
                )
                content = response.choices[0].message.content.strip()
                return self.parse_complete_soap_response(content)
            
            elif self.llm_provider == "google":
                response = self.client.generate_content(
                    f"{self.get_system_prompt()}\n\n{prompt}",
                    generation_config={
                        "max_output_tokens": 1500,
                        "temperature": 0.3
                    }
                )
                content = response.text.strip()
                return self.parse_complete_soap_response(content)
            
        except Exception as e:
            self.logger.error(f"Complete SOAP generation failed: {e}")
            # Fallback to individual section generation
            return self.generate_soap_sections_individually(transcript, segments)
    
    def create_complete_soap_prompt(self, transcript: str, segments: List[Dict[str, Any]]) -> str:
        """Create a prompt for generating all SOAP sections at once"""
        
        prompt = f"""Please analyze the following clinical transcript and generate a complete SOAP note with all four sections.

CLINICAL TRANSCRIPT:
{transcript}

Please provide your response in the following exact format:

SUBJECTIVE:
[Extract and summarize what the patient reports about their symptoms, concerns, medical history, and subjective experiences]

OBJECTIVE:
[Document observable findings, vital signs, physical examination results, and measurable data]

ASSESSMENT:
[Provide clinical impressions, diagnoses, and assessment of the patient's condition]

PLAN:
[Outline treatment plans, medications, follow-up instructions, and next steps]

Make sure each section is clearly labeled and contains relevant, medically accurate information from the transcript."""

        return prompt
    
    def parse_complete_soap_response(self, content: str) -> Dict[str, str]:
        """Parse the complete SOAP response into individual sections"""
        
        soap_notes = {
            "subjective": "",
            "objective": "",
            "assessment": "",
            "plan": ""
        }
        
        # Split by section headers
        sections = content.split('\n')
        current_section = None
        current_content = []
        
        for line in sections:
            line = line.strip()
            if line.upper().startswith('SUBJECTIVE:'):
                if current_section and current_content:
                    soap_notes[current_section] = '\n'.join(current_content).strip()
                current_section = 'subjective'
                current_content = [line.replace('SUBJECTIVE:', '').strip()]
            elif line.upper().startswith('OBJECTIVE:'):
                if current_section and current_content:
                    soap_notes[current_section] = '\n'.join(current_content).strip()
                current_section = 'objective'
                current_content = [line.replace('OBJECTIVE:', '').strip()]
            elif line.upper().startswith('ASSESSMENT:'):
                if current_section and current_content:
                    soap_notes[current_section] = '\n'.join(current_content).strip()
                current_section = 'assessment'
                current_content = [line.replace('ASSESSMENT:', '').strip()]
            elif line.upper().startswith('PLAN:'):
                if current_section and current_content:
                    soap_notes[current_section] = '\n'.join(current_content).strip()
                current_section = 'plan'
                current_content = [line.replace('PLAN:', '').strip()]
            elif current_section and line:
                current_content.append(line)
        
        # Don't forget the last section
        if current_section and current_content:
            soap_notes[current_section] = '\n'.join(current_content).strip()
        
        # Clean up any empty sections
        for section in soap_notes:
            if not soap_notes[section]:
                soap_notes[section] = f"No {section} information available from transcript."
        
        return soap_notes
    
    def generate_soap_sections_individually(self, transcript: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Fallback method to generate sections individually if batch generation fails"""
        soap_notes = {}
        
        for section in ["subjective", "objective", "assessment", "plan"]:
            soap_notes[section] = self.generate_soap_section(
                section, transcript, segments
            )
        
        return soap_notes

    def post_process_soap_notes(self, soap_notes: Dict[str, str]) -> Dict[str, str]:
        """Post-process and validate SOAP notes"""
        
        # Clean up formatting
        for section in soap_notes:
            if soap_notes[section]:
                # Remove any section headers that might be duplicated
                content = soap_notes[section]
                section_upper = section.upper()
                if content.upper().startswith(f"{section_upper}:"):
                    content = content[len(f"{section_upper}:"):].strip()
                
                # Clean up extra whitespace
                content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())
                soap_notes[section] = content
            
            # Ensure no section is completely empty
            if not soap_notes[section] or soap_notes[section].strip() == "":
                soap_notes[section] = f"No {section} information available from transcript."
        
        return soap_notes
    
    def generate_soap_fallback(self, transcript: str, segments: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate SOAP notes using rule-based approach when LLM is unavailable"""
        
        # Extract content from transcript
        lines = [line.strip() for line in transcript.split('\n') if line.strip()]
        
        # Initialize SOAP sections
        soap_notes = {
            "subjective": "Patient presents with complaints as documented in the encounter.",
            "objective": "Clinical findings and vital signs as documented.",
            "assessment": "Assessment based on clinical presentation.",
            "plan": "Treatment plan and follow-up as discussed."
        }
        
        # Try to extract some basic information
        patient_statements = []
        for line in lines:
            if 'patient:' in line.lower():
                content = line.split(':', 1)[1].strip()
                patient_statements.append(content)
        
        if patient_statements:
            soap_notes["subjective"] = "Patient reports: " + ". ".join(patient_statements[:3])
        
        return soap_notes
    
    def generate_section_fallback(self, section: str, transcript: str, segments: List[Dict[str, Any]]) -> str:
        """Generate fallback content for a specific section"""
        fallback_content = {
            "subjective": "Patient presents with complaints as documented in the encounter.",
            "objective": "Clinical findings and measurements as documented.",
            "assessment": "Clinical assessment based on presentation.",
            "plan": "Treatment plan and follow-up as discussed."
        }
        return fallback_content.get(section, f"No {section} information available.")
