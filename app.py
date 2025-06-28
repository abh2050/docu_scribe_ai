import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go

from agents.transcription_agent import TranscriptionAgent
from agents.context_agent import ContextAgent
from agents.scribe_agent import ScribeAgent
from agents.concept_agent import ConceptAgent
from agents.icd_mapper_agent import ICDMapperAgent
from agents.feedback_agent import FeedbackAgent
from agents.formatter_agent import FormatterAgent
from utils.fhir_formatter import FHIRFormatter
from evaluation.llmops_evaluator import LLMOpsEvaluator

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
        time.sleep(1)  # Simulate processing
        
        transcription_result = self.transcription_agent.process(transcript_text)
        agent_status["Transcription"] = "complete"
        results["transcription"] = transcription_result
        
        # Step 2: Context Analysis
        agent_status["Context Analysis"] = "running"
        self.display_agent_status(agent_status)
        time.sleep(1)
        
        context_result = self.context_agent.analyze(transcription_result["cleaned_text"])
        agent_status["Context Analysis"] = "complete"
        results["context"] = context_result
        
        # Step 3: Medical Scribing
        agent_status["Medical Scribing"] = "running"
        self.display_agent_status(agent_status)
        time.sleep(2)
        
        soap_notes = self.scribe_agent.generate_soap_notes(
            transcription_result["cleaned_text"],
            context_result["segments"]
        )
        agent_status["Medical Scribing"] = "complete"
        results["soap_notes"] = soap_notes
        
        # Step 4: Concept Extraction
        agent_status["Concept Extraction"] = "running"
        self.display_agent_status(agent_status)
        time.sleep(1)
        
        concepts = self.concept_agent.extract_concepts(transcription_result["cleaned_text"])
        agent_status["Concept Extraction"] = "complete"
        results["concepts"] = concepts
        
        # Step 5: ICD Mapping
        agent_status["ICD Mapping"] = "running"
        self.display_agent_status(agent_status)
        time.sleep(1)
        
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
        self.display_header()
        
        # Sidebar
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # Model selection
            llm_provider = st.selectbox(
                "LLM Provider",
                ["OpenAI", "Google", "Anthropic"],
                index=0
            )
            
            model_name = st.selectbox(
                "Model",
                ["gpt-4", "gpt-3.5-turbo", "gemini-pro", "claude-3-sonnet"],
                index=0
            )
            
            st.divider()
            
            # Example transcripts
            st.header("📁 Example Transcripts")
            if st.button("Load Hypertension Follow-up"):
                st.session_state.example_transcript = """
                Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?
                
                Patient: Good morning, Dr. Smith. I've been doing okay, but I've been having some headaches lately, especially in the mornings.
                
                Doctor: I see. When did these headaches start? And have you been taking your blood pressure medication regularly?
                
                Patient: The headaches started about two weeks ago. And yes, I've been taking my lisinopril every morning, 10mg as prescribed.
                
                Doctor: Good. Let me check your blood pressure today. *takes blood pressure* Your blood pressure is 150 over 95, which is higher than we'd like to see. 
                
                Patient: Is that bad? I've been trying to watch my salt intake like you suggested.
                
                Doctor: It's elevated, but we can manage this. The headaches could be related to the higher blood pressure. I think we need to increase your lisinopril to 20mg daily. Also, let's add some labs to check your kidney function.
                
                Patient: Okay, whatever you think is best. Should I be worried?
                
                Doctor: No need to worry. With the medication adjustment and continued lifestyle modifications, we should see improvement. I'd like to see you back in 4 weeks to recheck your blood pressure.
                """
            
            st.divider()
            
            # LLMOps Evaluation
            st.header("📊 LLMOps Evaluation")
            
            # Initialize evaluator if not exists
            if 'evaluator' not in st.session_state:
                st.session_state.evaluator = LLMOpsEvaluator()
            
            if st.button("🔍 Run Sample Evaluation"):
                with st.spinner("Running evaluation..."):
                    self.run_sample_evaluation()
            
            if st.session_state.get('processing_complete') and st.session_state.get('full_results'):
                if st.button("📈 Evaluate Current Results"):
                    with st.spinner("Evaluating current results..."):
                        self.evaluate_current_results()
        
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
                self.display_evaluation_results()
            
            # Final completion
            if st.session_state.agent_status.get("Human Review") == "running":
                if st.button("✅ Approve & Finalize", type="primary"):
                    st.session_state.agent_status["Human Review"] = "complete"
                    st.session_state.agent_status["Final Formatting"] = "complete"
                    st.balloons()
                    st.success("🎉 Clinical documentation completed and ready for EHR integration!")
    
    def run_sample_evaluation(self):
        """Run evaluation with sample data"""
        try:
            # Sample reference data
            reference_soap = {
                "subjective": "Patient reports persistent headache for 3 days, described as constant ache behind eyes. Associated with photophobia. Ibuprofen provides minimal relief.",
                "objective": "Blood pressure 150/95 mmHg (elevated). Patient appears uncomfortable.",
                "assessment": "Headache with hypertension. Possible tension headache vs. hypertensive headache.",
                "plan": "1. Blood pressure monitoring 2. Consider antihypertensive medication 3. Follow-up in 1 week 4. Return if symptoms worsen"
            }
            
            reference_concepts = [
                {"concept": "headache", "category": "symptom"},
                {"concept": "photophobia", "category": "symptom"},
                {"concept": "hypertension", "category": "condition"},
                {"concept": "ibuprofen", "category": "medication"}
            ]
            
            reference_icd_codes = [
                {"code": "R51.9", "description": "Headache, unspecified"},
                {"code": "I10", "description": "Essential hypertension"}
            ]
            
            # Generate sample predictions (using simple mock data for demo)
            generated_soap = {
                "subjective": "Patient complains of headache for several days. Photophobia present. Takes ibuprofen without relief.",
                "objective": "Elevated BP 150/95. Patient uncomfortable.",
                "assessment": "Headache likely related to hypertension.",
                "plan": "Increase antihypertensive medication. Follow-up needed."
            }
            
            generated_concepts = [
                {"concept": "headache", "category": "symptom"},
                {"concept": "photophobia", "category": "symptom"},
                {"concept": "hypertension", "category": "condition"}
            ]
            
            generated_icd_codes = [
                {"code": "R51.9", "description": "Headache, unspecified"},
                {"code": "I10", "description": "Essential hypertension"}
            ]
            
            # Run evaluations
            soap_scores = st.session_state.evaluator.evaluate_soap_notes(generated_soap, reference_soap)
            concept_scores = st.session_state.evaluator.evaluate_concept_extraction(generated_concepts, reference_concepts)
            icd_scores = st.session_state.evaluator.evaluate_icd_mapping(generated_icd_codes, reference_icd_codes)
            
            # Store results
            st.session_state.evaluation_results = {
                'soap_scores': soap_scores,
                'concept_scores': concept_scores,
                'icd_scores': icd_scores,
                'timestamp': datetime.now().isoformat()
            }
            
            # Display results
            st.success("✅ Sample evaluation completed!")
            self.display_evaluation_results()
            
        except Exception as e:
            st.error(f"❌ Error running evaluation: {str(e)}")
    
    def evaluate_current_results(self):
        """Evaluate the current processing results"""
        try:
            # Use simple reference data for demonstration
            reference_soap = {
                "subjective": "Patient reports symptoms and concerns discussed during visit.",
                "objective": "Clinical findings and measurements documented.",
                "assessment": "Clinical assessment and differential diagnosis provided.",
                "plan": "Treatment plan and follow-up recommendations outlined."
            }
            
            reference_concepts = [
                {"concept": "example", "category": "symptom"}
            ]
            
            reference_icd_codes = [
                {"code": "Z00.00", "description": "Encounter for general examination"}
            ]
            
            # Get current results
            current_soap = st.session_state.full_results.get('soap_notes', {})
            current_concepts = st.session_state.full_results.get('concepts', [])
            current_icd_codes = st.session_state.full_results.get('icd_codes', [])
            
            # Run evaluations
            soap_scores = st.session_state.evaluator.evaluate_soap_notes(current_soap, reference_soap)
            concept_scores = st.session_state.evaluator.evaluate_concept_extraction(current_concepts, reference_concepts)
            icd_scores = st.session_state.evaluator.evaluate_icd_mapping(current_icd_codes, reference_icd_codes)
            
            # Store results
            st.session_state.evaluation_results = {
                'soap_scores': soap_scores,
                'concept_scores': concept_scores,
                'icd_scores': icd_scores,
                'timestamp': datetime.now().isoformat()
            }
            
            st.success("✅ Current results evaluated!")
            self.display_evaluation_results()
            
        except Exception as e:
            st.error(f"❌ Error evaluating current results: {str(e)}")
    
    def display_evaluation_results(self):
        """Display evaluation results"""
        if 'evaluation_results' not in st.session_state:
            return
        
        results = st.session_state.evaluation_results
        
        st.subheader("📊 Evaluation Results")
        
        # Create metrics columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "SOAP BLEU Score",
                f"{results['soap_scores'].get('bleu_score', 0):.3f}",
                help="BLEU score measures similarity to reference text"
            )
            st.metric(
                "SOAP ROUGE Score", 
                f"{results['soap_scores'].get('rouge_score', 0):.3f}",
                help="ROUGE score measures overlap with reference text"
            )
        
        with col2:
            st.metric(
                "Concept Precision",
                f"{results['concept_scores'].get('precision', 0):.3f}",
                help="Precision of extracted medical concepts"
            )
            st.metric(
                "Concept F1 Score",
                f"{results['concept_scores'].get('f1_score', 0):.3f}",
                help="F1 score for concept extraction"
            )
        
        with col3:
            st.metric(
                "ICD Accuracy",
                f"{results['icd_scores'].get('accuracy', 0):.3f}",
                help="Accuracy of ICD code mapping"
            )
            st.metric(
                "ICD F1 Score",
                f"{results['icd_scores'].get('f1_score', 0):.3f}",
                help="F1 score for ICD code mapping"
            )
        
        # Detailed results in expander
        with st.expander("📋 Detailed Evaluation Results"):
            st.json(results)
