"""
LangGraph implementation for DocuScribe AI Agent Pipeline
This module provides a graph-based orchestration of the medical documentation agents
"""

from typing import Dict, Any, List, Tuple
try:
    from langgraph.graph import StateGraph, END
    LANGGRAPH_IMPORTS_AVAILABLE = True
except ImportError:
    LANGGRAPH_IMPORTS_AVAILABLE = False
    # Create dummy classes for type checking
    class StateGraph:
        def __init__(self, state_type): pass
        def add_node(self, name, func): pass
        def set_entry_point(self, name): pass
        def add_edge(self, start, end): pass
        def compile(self): return None
    
    END = "END"

from agents.transcription_agent import TranscriptionAgent
from agents.context_agent import ContextAgent
from agents.scribe_agent import ScribeAgent
from agents.concept_agent import ConceptAgent
from agents.icd_mapper_agent import ICDMapperAgent
from agents.feedback_agent import FeedbackAgent
from agents.formatter_agent import FormatterAgent


# Define initial state structure
def create_initial_state(transcript_text: str) -> Dict[str, Any]:
    """Create initial state for the pipeline - matches app.py structure exactly"""
    return {
        # Input
        "transcript_text": transcript_text,
        
        # Results matching app.py structure exactly
        "transcription": {},
        "context": {},
        "soap_notes": {},
        "concepts": [],
        "icd_codes": [],
        "metrics": {},
        
        # Agent status matching app.py exactly
        "agent_status": {
            "Transcription": "pending",
            "Context Analysis": "pending", 
            "Medical Scribing": "pending",
            "Concept Extraction": "pending",
            "ICD Mapping": "pending",
            "Human Review": "pending",
            "Final Formatting": "pending"
        },
        
        # Processing metadata
        "processing_start_time": None,
        "errors": []
    }


class DocuScribeLangGraphPipeline:
    """LangGraph-based pipeline for DocuScribe AI agents"""
    
    def __init__(self):
        if not LANGGRAPH_IMPORTS_AVAILABLE:
            raise ImportError("LangGraph is not installed. Please install with: pip install langgraph")
        
        self.agents = self._initialize_agents()
        self.graph = self._build_graph()
        
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agents - matching app.py structure"""
        return {
            "transcription": TranscriptionAgent(),
            "context": ContextAgent(),
            "scribe": ScribeAgent(),
            "concept": ConceptAgent(),
            "icd_mapper": ICDMapperAgent(),
            "feedback": FeedbackAgent(),
            "formatter": FormatterAgent()
        }
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow - matches app.py flow exactly"""
        
        # Create the graph - use dict as state type
        workflow = StateGraph(dict)
        
        # Add nodes (agents) - matching app.py sequence
        workflow.add_node("transcription", self._transcription_node)
        workflow.add_node("context_analysis", self._context_node)
        workflow.add_node("medical_scribing", self._scribe_node)
        workflow.add_node("concept_extraction", self._concept_node)
        workflow.add_node("icd_mapping", self._icd_node)
        workflow.add_node("metrics_calculation", self._metrics_node)
        
        # Define the workflow edges - exact sequence from app.py
        workflow.set_entry_point("transcription")
        workflow.add_edge("transcription", "context_analysis")
        workflow.add_edge("context_analysis", "medical_scribing")
        workflow.add_edge("medical_scribing", "concept_extraction")
        workflow.add_edge("concept_extraction", "icd_mapping")
        workflow.add_edge("icd_mapping", "metrics_calculation")
        workflow.add_edge("metrics_calculation", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _transcription_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process transcription - Step 1 from app.py"""
        try:
            # Set processing start time if not set
            if state["processing_start_time"] is None:
                import time
                state["processing_start_time"] = time.time()
            
            # Update agent status - matching app.py exactly
            state["agent_status"]["Transcription"] = "running"
            
            # Process transcription
            result = self.agents["transcription"].process(state["transcript_text"])
            state["transcription"] = result
            state["agent_status"]["Transcription"] = "complete"
            
        except Exception as e:
            state["errors"].append(f"Transcription error: {str(e)}")
            state["agent_status"]["Transcription"] = "error"
        
        return state
    
    def _context_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process context analysis - Step 2 from app.py"""
        try:
            # Update agent status
            state["agent_status"]["Context Analysis"] = "running"
            
            # Get cleaned text from transcription result
            cleaned_text = state["transcription"]["cleaned_text"]
            result = self.agents["context"].analyze(cleaned_text)
            state["context"] = result
            state["agent_status"]["Context Analysis"] = "complete"
            
        except Exception as e:
            state["errors"].append(f"Context analysis error: {str(e)}")
            state["agent_status"]["Context Analysis"] = "error"
        
        return state
    
    def _scribe_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process SOAP note generation - Step 3 from app.py"""
        try:
            # Update agent status
            state["agent_status"]["Medical Scribing"] = "running"
            
            # Generate SOAP notes using cleaned text and context segments
            cleaned_text = state["transcription"]["cleaned_text"]
            segments = state["context"]["segments"]
            result = self.agents["scribe"].generate_soap_notes(cleaned_text, segments)
            state["soap_notes"] = result
            state["agent_status"]["Medical Scribing"] = "complete"
            
        except Exception as e:
            state["errors"].append(f"Medical scribing error: {str(e)}")
            state["agent_status"]["Medical Scribing"] = "error"
        
        return state
    
    def _concept_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process concept extraction - Step 4 from app.py"""
        try:
            # Update agent status
            state["agent_status"]["Concept Extraction"] = "running"
            
            # Extract concepts from cleaned text
            cleaned_text = state["transcription"]["cleaned_text"]
            result = self.agents["concept"].extract_concepts(cleaned_text)
            state["concepts"] = result
            state["agent_status"]["Concept Extraction"] = "complete"
            
        except Exception as e:
            state["errors"].append(f"Concept extraction error: {str(e)}")
            state["agent_status"]["Concept Extraction"] = "error"
        
        return state
    
    def _icd_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process ICD mapping - Step 5 from app.py"""
        try:
            # Update agent status
            state["agent_status"]["ICD Mapping"] = "running"
            
            # Map concepts to ICD-10 codes
            concepts = state["concepts"]
            result = self.agents["icd_mapper"].map_to_icd10(concepts)
            state["icd_codes"] = result
            state["agent_status"]["ICD Mapping"] = "complete"
            
        except Exception as e:
            state["errors"].append(f"ICD mapping error: {str(e)}")
            state["agent_status"]["ICD Mapping"] = "error"
        
        return state
    
    def _metrics_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics - matches app.py metrics calculation"""
        try:
            import time
            from datetime import datetime
            
            # Calculate processing time
            end_time = time.time()
            processing_time = end_time - state["processing_start_time"]
            
            # Calculate confidence score - same logic as app.py
            concepts = state["concepts"]
            confidence_score = (sum([concept.get("confidence", 0.8) for concept in concepts]) / len(concepts)) if concepts else 0.8
            
            # Build metrics exactly like app.py
            metrics = {
                "processing_time": processing_time,
                "confidence_score": confidence_score,
                "concepts_extracted": len(concepts),
                "icd_codes_suggested": len(state["icd_codes"]),
                "timestamp": datetime.now().isoformat()
            }
            
            state["metrics"] = metrics
            
            # Set Human Review status as running (like app.py)
            state["agent_status"]["Human Review"] = "running"
            
        except Exception as e:
            state["errors"].append(f"Metrics calculation error: {str(e)}")
        
        return state
    
    def process_transcript(self, transcript_text: str) -> Dict[str, Any]:
        """Process a transcript through the LangGraph pipeline - returns results dict like manual pipeline"""
        
        # Initialize state
        initial_state = create_initial_state(transcript_text)
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return results in the same structure as manual pipeline for compatibility
        return {
            "transcription": final_state["transcription"],
            "context": final_state["context"], 
            "soap_notes": final_state["soap_notes"],
            "concepts": final_state["concepts"],
            "icd_codes": final_state["icd_codes"],
            "metrics": final_state["metrics"],
            "agent_status": final_state["agent_status"],
            "errors": final_state["errors"]
        }
    
    def process_transcript_with_status(self, transcript_text: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Process transcript and return results + agent_status tuple like app.py"""
        
        # Initialize state
        initial_state = create_initial_state(transcript_text)
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return results and agent_status tuple matching app.py process_transcript
        results = {
            "transcription": final_state["transcription"],
            "context": final_state["context"], 
            "soap_notes": final_state["soap_notes"],
            "concepts": final_state["concepts"],
            "icd_codes": final_state["icd_codes"],
            "metrics": final_state["metrics"]
        }
        
        agent_status = final_state["agent_status"]
        
        return results, agent_status
    
    def get_pipeline_status(self, state: Dict[str, Any]) -> Dict[str, str]:
        """Get current pipeline status"""
        return state.get("agent_status", {})
    
    def is_pipeline_complete(self, state: Dict[str, Any]) -> bool:
        """Check if pipeline processing is complete"""
        agent_status = state.get("agent_status", {})
        required_agents = ["Transcription", "Context Analysis", "Medical Scribing", 
                          "Concept Extraction", "ICD Mapping"]
        
        return all(agent_status.get(agent) == "complete" for agent in required_agents)


# Example usage function
def create_pipeline() -> DocuScribeLangGraphPipeline:
    """Create and return a DocuScribe LangGraph pipeline instance"""
    if not LANGGRAPH_IMPORTS_AVAILABLE:
        raise ImportError("LangGraph is not available. Please install with: pip install langgraph")
    
    return DocuScribeLangGraphPipeline()


# Usage example
if __name__ == "__main__":
    pipeline = DocuScribeLangGraphPipeline()
    
    # Test transcript
    test_transcript = """
    Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?
    Patient: Good morning, Dr. Smith. I've been having some headaches lately, especially in the mornings.
    Doctor: When did these headaches start? Have you been taking your blood pressure medication regularly?
    Patient: The headaches started about two weeks ago. Yes, I've been taking my lisinopril 10mg every morning as prescribed.
    """
    
    # Process through pipeline
    results, agent_status = pipeline.process_transcript_with_status(test_transcript)
    print("Pipeline completed successfully!")
    print(f"Agent Status: {agent_status}")
    print(f"Processing Time: {results['metrics']['processing_time']:.2f}s")
