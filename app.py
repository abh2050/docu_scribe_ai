import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
import os

from agents.transcription_agent import TranscriptionAgent
from agents.context_agent import ContextAgent
from agents.scribe_agent import ScribeAgent
from agents.concept_agent import ConceptAgent
from agents.icd_mapper_agent import ICDMapperAgent
from agents.feedback_agent import FeedbackAgent
from agents.formatter_agent import FormatterAgent
from utils.fhir_formatter import FHIRFormatter

# Page configuration
st.set_page_config(
    page_title="DocuScribe AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .agent-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
        color: white;
    }
    
    .agent-running {
        background-color: #ffa500;
    }
    
    .agent-complete {
        background-color: #28a745;
    }
    
    .agent-pending {
        background-color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

class DocuScribeApp:
    def __init__(self):
        self.initialize_session_state()
        self.initialize_agents()
        
        # Initialize example transcript options
        self.example_options = {
            "Hypertension Follow-up": "data/example_transcripts/hypertension_followup.txt",
            "Diabetes Management": "data/example_transcripts/diabetes_management.txt",
            "Knee Osteoarthritis": "data/example_transcripts/knee_osteoarthritis.txt",
            "Pneumonia Case": "data/example_transcripts/pneumonia_case.txt",
            "Pediatric Ear Infection": "data/example_transcripts/pediatric_ear_infection.txt",
            "Migraine Consultation": "data/example_transcripts/migraine_consultation.txt",
            "Allergic Reaction": "data/example_transcripts/allergic_reaction.txt"
        }
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'soap_notes' not in st.session_state:
            st.session_state.soap_notes = {}
        if 'extracted_concepts' not in st.session_state:
            st.session_state.extracted_concepts = []
        if 'icd_codes' not in st.session_state:
            st.session_state.icd_codes = []
        if 'processing_metrics' not in st.session_state:
            st.session_state.processing_metrics = {}
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {}
    
    def initialize_agents(self):
        """Initialize all agents"""
        try:
            self.transcription_agent = TranscriptionAgent()
            self.context_agent = ContextAgent()
            self.scribe_agent = ScribeAgent()
            self.concept_agent = ConceptAgent()
            self.icd_mapper_agent = ICDMapperAgent()
            self.feedback_agent = FeedbackAgent()
            self.formatter_agent = FormatterAgent()
            self.fhir_formatter = FHIRFormatter()
        except Exception as e:
            st.error(f"Failed to initialize agents: {str(e)}")
    
    def display_header(self):
        """Display the main header"""
        st.markdown("""
        <div class="main-header">
            <h1>🩺 DocuScribe AI</h1>
            <p>Agentic Ambient Scribing System for Clinical Encounters</p>
        </div>
        """, unsafe_allow_html=True)
    
    def display_agent_status(self, agent_statuses: Dict[str, str]):
        """Display the status of each agent"""
        st.subheader("🤖 Agent Pipeline Status")
        
        agents = [
            "Transcription", "Context Analysis", "Medical Scribing",
            "Concept Extraction", "ICD Mapping", "Human Review", "Final Formatting"
        ]
        
        cols = st.columns(len(agents))
        
        for i, agent in enumerate(agents):
            with cols[i]:
                status = agent_statuses.get(agent, "pending")
                status_class = f"agent-{status}"
                
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "complete": "✅"
                }.get(status, "⏳")
                
                st.markdown(f"""
                <div class="agent-status {status_class}">
                    {status_emoji} {agent}
                </div>
                """, unsafe_allow_html=True)
    
    def process_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Process the transcript through the agent pipeline"""
        start_time = time.time()
        results = {}
        
        # Update agent status
        agent_status = {agent: "pending" for agent in [
            "Transcription", "Context Analysis", "Medical Scribing",
            "Concept Extraction", "ICD Mapping", "Human Review", "Final Formatting"
        ]}
        
        # Step 1: Transcription (already have text)
        agent_status["Transcription"] = "running"
        self.display_agent_status(agent_status)
        
        transcription_result = self.transcription_agent.process(transcript_text)
        agent_status["Transcription"] = "complete"
        results["transcription"] = transcription_result
        
        # Step 2: Context Analysis
        agent_status["Context Analysis"] = "running"
        self.display_agent_status(agent_status)
        
        context_result = self.context_agent.analyze(transcription_result["cleaned_text"])
        agent_status["Context Analysis"] = "complete"
        results["context"] = context_result
        
        # Step 3: Medical Scribing
        agent_status["Medical Scribing"] = "running"
        self.display_agent_status(agent_status)
        
        soap_notes = self.scribe_agent.generate_soap_notes(
            transcription_result["cleaned_text"],
            context_result["segments"]
        )
        agent_status["Medical Scribing"] = "complete"
        results["soap_notes"] = soap_notes
        
        # Step 4: Concept Extraction
        agent_status["Concept Extraction"] = "running"
        self.display_agent_status(agent_status)
        
        concepts = self.concept_agent.extract_concepts(transcription_result["cleaned_text"])
        agent_status["Concept Extraction"] = "complete"
        results["concepts"] = concepts
        
        # Step 5: ICD Mapping
        agent_status["ICD Mapping"] = "running"
        self.display_agent_status(agent_status)
        
        icd_codes = self.icd_mapper_agent.map_to_icd10(concepts)
        agent_status["ICD Mapping"] = "complete"
        results["icd_codes"] = icd_codes
        
        # Calculate metrics
        end_time = time.time()
        processing_time = end_time - start_time
        
        metrics = {
            "processing_time": processing_time,
            "confidence_score": sum([concept.get("confidence", 0.8) for concept in concepts]) / len(concepts) if concepts else 0.8,
            "concepts_extracted": len(concepts),
            "icd_codes_suggested": len(icd_codes),
            "timestamp": datetime.now().isoformat()
        }
        
        results["metrics"] = metrics
        agent_status["Human Review"] = "running"
        
        return results, agent_status
    
    def display_soap_editor(self, soap_notes: Dict[str, str]) -> Dict[str, str]:
        """Display editable SOAP notes"""
        st.subheader("📝 SOAP Notes - Review & Edit")
        
        edited_soap = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Subjective**")
            edited_soap["subjective"] = st.text_area(
                "Subjective",
                value=soap_notes.get("subjective", ""),
                height=150,
                label_visibility="collapsed"
            )
            
            st.markdown("**Assessment**")
            edited_soap["assessment"] = st.text_area(
                "Assessment",
                value=soap_notes.get("assessment", ""),
                height=150,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**Objective**")
            edited_soap["objective"] = st.text_area(
                "Objective",
                value=soap_notes.get("objective", ""),
                height=150,
                label_visibility="collapsed"
            )
            
            st.markdown("**Plan**")
            edited_soap["plan"] = st.text_area(
                "Plan",
                value=soap_notes.get("plan", ""),
                height=150,
                label_visibility="collapsed"
            )
        
        return edited_soap
    
    def display_concepts_and_codes(self, concepts: List[Dict], icd_codes: List[Dict]):
        """Display extracted concepts and ICD codes"""
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔍 Extracted Medical Concepts")
            if concepts:
                concepts_df = pd.DataFrame(concepts)
                st.dataframe(concepts_df, use_container_width=True)
            else:
                st.info("No medical concepts extracted")
        
        with col2:
            st.subheader("🏥 Suggested ICD-10 Codes")
            if icd_codes:
                icd_df = pd.DataFrame(icd_codes)
                st.dataframe(icd_df, use_container_width=True)
            else:
                st.info("No ICD-10 codes suggested")
    
    def display_metrics(self, metrics: Dict[str, Any]):
        """Display processing metrics"""
        st.subheader("📊 Processing Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Processing Time",
                f"{metrics.get('processing_time', 0):.2f}s"
            )
        
        with col2:
            st.metric(
                "Confidence Score",
                f"{metrics.get('confidence_score', 0):.1%}"
            )
        
        with col3:
            st.metric(
                "Concepts Extracted",
                metrics.get('concepts_extracted', 0)
            )
        
        with col4:
            st.metric(
                "ICD Codes",
                metrics.get('icd_codes_suggested', 0)
            )
    
    def display_fhir_output(self, results: Dict[str, Any]):
        """Display FHIR-formatted output"""
        st.subheader("🔗 FHIR Export")
        
        fhir_data = self.fhir_formatter.format_to_fhir(results)
        
        st.json(fhir_data)
        
        # Download button
        json_str = json.dumps(fhir_data, indent=2)
        st.download_button(
            label="📥 Download FHIR JSON",
            data=json_str,
            file_name=f"clinical_note_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def run(self):
        """Main application loop"""
        # Initialize session state
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'soap_notes' not in st.session_state:
            st.session_state.soap_notes = {}
        if 'extracted_concepts' not in st.session_state:
            st.session_state.extracted_concepts = []
        if 'icd_codes' not in st.session_state:
            st.session_state.icd_codes = []
        if 'processing_metrics' not in st.session_state:
            st.session_state.processing_metrics = {}
        if 'agent_status' not in st.session_state:
            st.session_state.agent_status = {}
        if 'full_results' not in st.session_state:
            st.session_state.full_results = {}
            
        self.display_header()
        
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Clear chat and memory button
            if st.button("🗑️ Clear Chat & Memory", type="secondary", use_container_width=True):
                self.clear_session_state()
            
            st.divider()
            
            # Model selection
            llm_provider = st.selectbox(
                "LLM Provider",
                ["OpenAI", "Google"],
                index=0
            )
            
            model_name = st.selectbox(
                "Model",
                ["gpt-3.5-turbo", "gpt-4", "gemini-pro"],
                index=0
            )
            
            st.divider()
            
            # Example transcripts
            st.header("📁 Example Transcripts")
            
            # Function to load transcript from file
            def load_transcript_from_file(file_path):
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except Exception as e:
                    st.error(f"Failed to load transcript: {e}")
                    return ""
            
            # Example transcript selector
            example_options = self.example_options
            
            # Create columns for a more compact layout
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Load Hypertension Follow-up"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Hypertension Follow-up"])
                
                if st.button("Load Knee Osteoarthritis"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Knee Osteoarthritis"])

                if st.button("Load Migraine Consultation"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Migraine Consultation"])
            
            with col2:
                if st.button("Load Diabetes Management"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Diabetes Management"])
                
                if st.button("Load Pneumonia Case"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Pneumonia Case"])
                
                if st.button("Load Allergic Reaction"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Allergic Reaction"])
            
            with col3:
                if st.button("Load Pediatric Ear Infection"):
                    st.session_state.example_transcript = load_transcript_from_file(example_options["Pediatric Ear Infection"])
            
            # Add information about example transcripts
            with st.expander("About Example Transcripts"):
                st.markdown("""
                These example transcripts demonstrate different medical scenarios:
                
                - **Hypertension Follow-up**: Patient with elevated blood pressure and headaches
                - **Diabetes Management**: Patient struggling with glucose control
                - **Knee Osteoarthritis**: Patient with progressive joint pain and inflammation
                - **Pneumonia Case**: Patient with respiratory infection symptoms
                - **Pediatric Ear Infection**: Young child with recurring ear infections
                - **Migraine Consultation**: Patient with classic migraine symptoms and triggers
                - **Allergic Reaction**: Patient experiencing allergic reaction to seafood
                
                You can also load custom samples from the `/data/example_transcripts/` folder or browse all examples in the [Example Transcripts](/example_transcripts) page.
                """)
            
            st.divider()
            
            # LLM-based Evaluation
            st.header("🤖 LLM Evaluation")
            
            if st.session_state.get('processing_complete') and st.session_state.get('full_results'):
                if st.button("🤖 Get AI Feedback", help="Use AI to provide qualitative assessment"):
                    with st.spinner("Running LLM-based evaluation..."):
                        self.run_llm_evaluation_only()
        
        # Main content area
        st.header("📋 Clinical Transcript Input")
        
        # Transcript input
        transcript_input = st.text_area(
            "Paste or type the clinical encounter transcript:",
            value=st.session_state.get('example_transcript', ''),
            height=200,
            placeholder="Enter the doctor-patient conversation transcript here..."
        )
        
        # Process button
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🚀 Process Transcript", type="primary", use_container_width=True):
                if transcript_input.strip():
                    with st.spinner("Processing transcript through agent pipeline..."):
                        try:
                            results, agent_status = self.process_transcript(transcript_input)
                            
                            # Store results in session state
                            st.session_state.processing_complete = True
                            st.session_state.soap_notes = results["soap_notes"]
                            st.session_state.extracted_concepts = results["concepts"]
                            st.session_state.icd_codes = results["icd_codes"]
                            st.session_state.processing_metrics = results["metrics"]
                            st.session_state.agent_status = agent_status
                            st.session_state.full_results = results
                            
                            st.success("✅ Processing complete!")
                            
                        except Exception as e:
                            st.error(f"❌ Error processing transcript: {str(e)}")
                else:
                    st.warning("⚠️ Please enter a transcript before processing.")
        
        with col2:
            if st.button("🗑️ Clear All", type="secondary", use_container_width=True, help="Clear all data and start fresh"):
                self.clear_session_state()
        
        # Display results if processing is complete
        if st.session_state.processing_complete:
            # Agent status
            self.display_agent_status(st.session_state.agent_status)
            
            st.divider()
            
            # SOAP Notes Editor
            edited_soap = self.display_soap_editor(st.session_state.soap_notes)
            
            # Update button
            if st.button("💾 Update SOAP Notes"):
                st.session_state.soap_notes = edited_soap
                st.session_state.full_results["soap_notes"] = edited_soap
                st.success("SOAP notes updated!")
            
            st.divider()
            
            # Concepts and ICD codes
            self.display_concepts_and_codes(
                st.session_state.extracted_concepts,
                st.session_state.icd_codes
            )
            
            st.divider()
            
            # Metrics
            self.display_metrics(st.session_state.processing_metrics)
            
            st.divider()
            
            # FHIR Output
            if hasattr(st.session_state, 'full_results'):
                self.display_fhir_output(st.session_state.full_results)
            
            # Evaluation Results
            if 'evaluation_results' in st.session_state:
                st.divider()
                self.display_llm_evaluation_results()
            
            # Final completion
            if st.session_state.agent_status.get("Human Review") == "running":
                if st.button("✅ Approve & Finalize", type="primary"):
                    st.session_state.agent_status["Human Review"] = "complete"
                    st.session_state.agent_status["Final Formatting"] = "complete"
                    st.balloons()
                    st.success("🎉 Clinical documentation completed and ready for EHR integration!")
    
    def run_llm_evaluation_only(self):
        """Run LLM-based evaluation on current results without traditional metrics"""
        try:
            # Get current transcript and determine type
            current_transcript = st.session_state.get('example_transcript', '')
            transcript_type = "General Medical Encounter"
            
            # Try to determine which example transcript is being used
            for transcript_name, file_path in self.example_options.items():
                try:
                    with open(file_path, 'r') as f:
                        file_content = f.read()
                        if current_transcript and file_content.strip() == current_transcript.strip():
                            transcript_type = transcript_name
                            break
                except Exception:
                    pass
            
            # Get current results
            current_soap = st.session_state.full_results.get('soap_notes', {})
            current_concepts = st.session_state.full_results.get('concepts', [])
            current_icd_codes = st.session_state.full_results.get('icd_codes', [])
            
            # Run LLM evaluation
            llm_result = self.evaluate_with_llm_simple(
                current_soap, current_concepts, current_icd_codes, transcript_type, current_transcript
            )
            
            # Store evaluation results
            st.session_state.evaluation_results = {
                'llm_evaluation': llm_result,
                'timestamp': datetime.now().isoformat()
            }
            
            st.success("✅ AI evaluation completed!")
            self.display_llm_evaluation_results()
            
        except Exception as e:
            st.error(f"❌ Error running AI evaluation: {str(e)}")
    
    def evaluate_with_llm_simple(self, generated_soap: Dict[str, str], generated_concepts: List[Dict], 
                          generated_icd_codes: List[Dict], transcript_type: str, transcript: str) -> Dict[str, Any]:
        """Use LLM to evaluate the quality of generated medical documentation without reference data"""
        try:
            # Format input for LLM
            concepts_text = ", ".join([f"{c.get('concept', '')} ({c.get('category', '')})" for c in generated_concepts])
            icd_codes_text = ", ".join([f"{c.get('code', '')} - {c.get('description', '')}" for c in generated_icd_codes])
            
            prompt = f"""
You are an expert medical evaluator judging the quality of AI-generated medical documentation for a {transcript_type} encounter.

ORIGINAL TRANSCRIPT:
{transcript[:500]}...

AI-GENERATED SOAP NOTES:
Subjective: {generated_soap.get('subjective', 'N/A')}
Objective: {generated_soap.get('objective', 'N/A')}
Assessment: {generated_soap.get('assessment', 'N/A')}
Plan: {generated_soap.get('plan', 'N/A')}

AI-EXTRACTED MEDICAL CONCEPTS:
{concepts_text}

AI-SUGGESTED ICD CODES:
{icd_codes_text}

Please evaluate the AI-generated medical documentation focusing on:
1. **Clinical Accuracy**: Are the medical facts correctly captured from the transcript?
2. **Completeness**: Did the AI capture all important information from the encounter?
3. **Relevance**: Is all included information medically relevant?
4. **Clarity**: Are the notes clear, concise, and well-organized?
5. **Professional Standards**: Do the notes meet clinical documentation standards?

Provide a structured evaluation with:
- Overall Quality Score (1-10)
- Key Strengths (2-3 points)
- Areas for Improvement (2-3 points)
- Specific recommendations for better documentation

Format your response as a professional clinical evaluation report.
"""
            
            # Try to use OpenAI for evaluation
            if not hasattr(self, 'openai_client'):
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.openai_client = openai.OpenAI(api_key=api_key)
                else:
                    return {"error": "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."}
            
            # Call the OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert medical evaluator specializing in clinical documentation quality assessment."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Extract the LLM's evaluation
            llm_evaluation = response.choices[0].message.content
            
            # Return the evaluation
            return {
                "llm_evaluation": llm_evaluation,
                "model_used": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return {"error": f"Error using LLM for evaluation: {str(e)}"}
    
    def display_llm_evaluation_results(self):
        """Display LLM evaluation results"""
        if 'evaluation_results' not in st.session_state:
            return
        
        results = st.session_state.evaluation_results
        
        st.subheader("🤖 AI Medical Documentation Evaluation")
        
        # Display LLM evaluation results
        if results.get('llm_evaluation'):
            if 'error' in results['llm_evaluation']:
                st.error(f"❌ {results['llm_evaluation']['error']}")
            else:
                st.markdown(results['llm_evaluation']['llm_evaluation'])
                st.caption(f"Evaluated using: {results['llm_evaluation']['model_used']}")
        
        # Detailed results in expander
        with st.expander("📋 Raw Evaluation Data"):
            st.json(results)

    def clear_session_state(self):
        """Clear all session state to reset the app for a new transcription"""
        # List of all session state keys to clear
        keys_to_clear = [
            'processing_complete',
            'soap_notes',
            'extracted_concepts',
            'icd_codes',
            'processing_metrics',
            'agent_status',
            'full_results',
            'evaluation_results',
            'example_transcript',
            'llm_provider',
            'model_name'
        ]
        
        # Clear each key
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
        
        # Re-initialize basic session state
        self.initialize_session_state()
        
        st.success("✅ Chat and memory cleared! Ready for new transcription.")
        st.rerun()  # Refresh the app to show cleared state


def main():
    """Main function to run the DocuScribe AI application"""
    app = DocuScribeApp()
    app.run()


if __name__ == "__main__":
    main()
