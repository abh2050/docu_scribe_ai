"""
Enhanced DocuScribe App with LangGraph integration option
"""

import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import plotly.express as px
import plotly.graph_objects as go
import os

# Import both pipeline options
from agents.transcription_agent import TranscriptionAgent
from agents.context_agent import ContextAgent
from agents.scribe_agent import ScribeAgent
from agents.concept_agent import ConceptAgent
from agents.icd_mapper_agent import ICDMapperAgent
from agents.feedback_agent import FeedbackAgent
from agents.formatter_agent import FormatterAgent
from utils.fhir_formatter import FHIRFormatter

# Try to import LangGraph pipeline
try:
    from langgraph_pipeline import DocuScribeLangGraphPipeline
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False

class DocuScribeApp:
    """Enhanced DocuScribe Application with LangGraph support"""
    
    def __init__(self):
        self.pipeline_mode = self._get_pipeline_mode()
        
        if self.pipeline_mode == "langgraph" and LANGGRAPH_AVAILABLE:
            self.langgraph_pipeline = DocuScribeLangGraphPipeline()
            st.success("🔄 LangGraph pipeline initialized successfully!")
        else:
            # Initialize individual agents (original approach)
            self.transcription_agent = TranscriptionAgent()
            self.context_agent = ContextAgent()
            self.scribe_agent = ScribeAgent()
            self.concept_agent = ConceptAgent()
            self.icd_mapper_agent = ICDMapperAgent()
            self.feedback_agent = FeedbackAgent()
            self.formatter_agent = FormatterAgent()
            self.fhir_formatter = FHIRFormatter()
            
            if self.pipeline_mode == "langgraph":
                st.warning("⚠️ LangGraph not available, falling back to manual orchestration")
    
    def _get_pipeline_mode(self) -> str:
        """Get pipeline mode from environment or sidebar"""
        # Check environment variable first
        env_mode = os.getenv("PIPELINE_MODE", "manual")
        
        # Allow user override in sidebar
        with st.sidebar:
            st.subheader("🔧 Pipeline Configuration")
            
            if LANGGRAPH_AVAILABLE:
                mode_options = ["manual", "langgraph"]
                mode_help = """
                - **Manual**: Original sequential agent orchestration
                - **LangGraph**: Graph-based workflow with better error handling and state management
                """
            else:
                mode_options = ["manual"]
                mode_help = "LangGraph not available. Install with: `pip install langgraph`"
            
            selected_mode = st.selectbox(
                "Pipeline Mode",
                options=mode_options,
                index=mode_options.index(env_mode) if env_mode in mode_options else 0,
                help=mode_help
            )
            
            return selected_mode
    
    def process_transcript_langgraph(self, transcript_text: str) -> Dict[str, Any]:
        """Process transcript using LangGraph pipeline"""
        st.info("🔄 Processing with LangGraph pipeline...")
        
        start_time = time.time()
        
        # Process through LangGraph
        results = self.langgraph_pipeline.process_transcript(transcript_text)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Add metrics
        concepts = results.get("concepts", [])
        icd_codes = results.get("icd_codes", [])
        
        metrics = {
            "processing_time": processing_time,
            "confidence_score": sum([concept.get("confidence", 0.8) for concept in concepts]) / len(concepts) if concepts else 0.8,
            "concepts_extracted": len(concepts),
            "icd_codes_suggested": len(icd_codes),
            "timestamp": datetime.now().isoformat(),
            "pipeline_mode": "langgraph"
        }
        
        results["metrics"] = metrics
        
        # Display agent status
        self.display_langgraph_status(results.get("agent_status", {}))
        
        if results.get("errors"):
            st.error(f"Pipeline errors: {results['errors']}")
        
        return results
    
    def process_transcript_manual(self, transcript_text: str) -> Dict[str, Any]:
        """Process transcript using manual orchestration (original method)"""
        st.info("🔄 Processing with manual orchestration...")
        
        start_time = time.time()
        results = {}
        
        # Update agent status
        agent_status = {agent: "pending" for agent in [
            "Transcription", "Context Analysis", "Medical Scribing",
            "Concept Extraction", "ICD Mapping", "Human Review", "Final Formatting"
        ]}
        
        # Step 1: Transcription
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
            "timestamp": datetime.now().isoformat(),
            "pipeline_mode": "manual"
        }
        
        results["metrics"] = metrics
        agent_status["Human Review"] = "running"
        
        return results, agent_status
    
    def process_transcript(self, transcript_text: str):
        """Main method to process transcript - routes to appropriate pipeline"""
        if self.pipeline_mode == "langgraph" and LANGGRAPH_AVAILABLE:
            return self.process_transcript_langgraph(transcript_text)
        else:
            return self.process_transcript_manual(transcript_text)
    
    def display_langgraph_status(self, agent_status: Dict[str, str]):
        """Display LangGraph agent status"""
        st.subheader("🔄 LangGraph Agent Pipeline Status")
        
        status_cols = st.columns(len(agent_status))
        
        for i, (agent, status) in enumerate(agent_status.items()):
            with status_cols[i]:
                if status == "complete":
                    st.success(f"✅ {agent.title()}")
                elif status == "running":
                    st.info(f"🔄 {agent.title()}")
                elif status == "error":
                    st.error(f"❌ {agent.title()}")
                else:
                    st.grey(f"⏳ {agent.title()}")
    
    def display_agent_status(self, agent_status: Dict[str, str]):
        """Display manual pipeline agent status"""
        st.subheader("🔄 Agent Pipeline Status")
        
        status_cols = st.columns(len(agent_status))
        
        for i, (agent, status) in enumerate(agent_status.items()):
            with status_cols[i]:
                if status == "complete":
                    st.success(f"✅ {agent}")
                elif status == "running":
                    st.info(f"🔄 {agent}")
                else:
                    st.grey(f"⏳ {agent}")
    
    def display_pipeline_comparison(self):
        """Display comparison between pipeline modes"""
        st.subheader("🔄 Pipeline Modes Comparison")
        
        comparison_data = {
            "Feature": [
                "Orchestration",
                "Error Handling", 
                "State Management",
                "Parallel Processing",
                "Workflow Visualization",
                "Debugging",
                "Scalability"
            ],
            "Manual Pipeline": [
                "Sequential function calls",
                "Basic try-catch",
                "Session state variables", 
                "Limited",
                "Custom status display",
                "Log-based",
                "Manual scaling"
            ],
            "LangGraph Pipeline": [
                "Graph-based workflow",
                "Robust error recovery",
                "Automatic state management",
                "Built-in support",
                "Graph visualization",
                "Built-in debugging",
                "Auto-scaling"
            ]
        }
        
        df = pd.DataFrame(comparison_data)
        st.table(df)
    
    def run(self):
        """Main application run method"""
        # Display header
        st.markdown(
            """
            <div class="main-header">
                <h1>🩺 DocuScribe AI - Agentic Ambient Scribing System</h1>
                <p>Transform clinical conversations into structured medical documentation</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Pipeline mode indicator
        if self.pipeline_mode == "langgraph":
            st.info(f"🔄 **Active Pipeline**: LangGraph (Graph-based orchestration)")
        else:
            st.info(f"🔄 **Active Pipeline**: Manual (Sequential orchestration)")
        
        # Main interface
        with st.container():
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 Clinical Transcript Input")
                transcript_text = st.text_area(
                    "Enter or paste the clinical conversation transcript:",
                    height=300,
                    placeholder="Doctor: Good morning, how are you feeling today?\nPatient: I've been having some headaches..."
                )
                
                if st.button("🚀 Process Transcript", type="primary"):
                    if transcript_text.strip():
                        with st.spinner("Processing transcript through agent pipeline..."):
                            results = self.process_transcript(transcript_text)
                            st.session_state.results = results
                            st.success("✅ Processing completed!")
                    else:
                        st.warning("Please enter a transcript to process.")
            
            with col2:
                st.subheader("🔧 Pipeline Information")
                self.display_pipeline_comparison()
                
                if st.button("🔄 Switch Pipeline Mode"):
                    if self.pipeline_mode == "manual":
                        if LANGGRAPH_AVAILABLE:
                            st.session_state.pipeline_mode = "langgraph"
                            st.experimental_rerun()
                        else:
                            st.error("LangGraph not available")
                    else:
                        st.session_state.pipeline_mode = "manual"
                        st.experimental_rerun()
        
        # Display results if available
        if hasattr(st.session_state, 'results') and st.session_state.results:
            self.display_results(st.session_state.results)
    
    def display_results(self, results: Dict[str, Any]):
        """Display processing results"""
        st.subheader("📊 Processing Results")
        
        # Metrics
        if "metrics" in results:
            metrics = results["metrics"]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Processing Time", f"{metrics.get('processing_time', 0):.2f}s")
            with col2:
                st.metric("Confidence Score", f"{metrics.get('confidence_score', 0):.2f}")
            with col3:
                st.metric("Concepts Extracted", metrics.get('concepts_extracted', 0))
            with col4:
                st.metric("ICD Codes", metrics.get('icd_codes_suggested', 0))
        
        # SOAP Notes
        if "soap_notes" in results:
            st.subheader("📝 SOAP Notes")
            soap_notes = results["soap_notes"]
            
            tab1, tab2, tab3, tab4 = st.tabs(["Subjective", "Objective", "Assessment", "Plan"])
            
            with tab1:
                st.write(soap_notes.get("subjective", "No subjective data"))
            with tab2:
                st.write(soap_notes.get("objective", "No objective data"))
            with tab3:
                st.write(soap_notes.get("assessment", "No assessment data"))
            with tab4:
                st.write(soap_notes.get("plan", "No plan data"))
        
        # Concepts and ICD codes
        col1, col2 = st.columns(2)
        
        with col1:
            if "concepts" in results:
                st.subheader("🔍 Extracted Concepts")
                concepts_df = pd.DataFrame(results["concepts"])
                if not concepts_df.empty:
                    st.dataframe(concepts_df)
                else:
                    st.write("No concepts extracted")
        
        with col2:
            if "icd_codes" in results:
                st.subheader("🏥 ICD-10 Codes")
                icd_df = pd.DataFrame(results["icd_codes"])
                if not icd_df.empty:
                    st.dataframe(icd_df)
                else:
                    st.write("No ICD codes suggested")


if __name__ == "__main__":
    app = DocuScribeApp()
    app.run()
