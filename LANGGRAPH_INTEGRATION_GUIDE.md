# LangGraph Integration Guide for DocuScribe AI

## Overview
This guide explains how to integrate LangGraph into the DocuScribe AI system for better agent orchestration and workflow management.

## Why LangGraph?

### Current Manual Orchestration Issues:
1. **Sequential Processing**: Agents run one after another with no parallelization
2. **Error Handling**: Limited error recovery and rollback capabilities
3. **State Management**: Manual session state management in Streamlit
4. **Debugging**: Difficult to trace agent execution and identify bottlenecks
5. **Scalability**: Hard to add conditional logic or parallel execution paths

### LangGraph Benefits:
1. **Graph-based Workflow**: Define complex agent relationships and dependencies
2. **Automatic State Management**: Built-in state passing between agents
3. **Error Recovery**: Robust error handling with retry mechanisms
4. **Parallel Execution**: Run independent agents simultaneously
5. **Conditional Routing**: Route to different agents based on conditions
6. **Workflow Visualization**: Visual representation of the agent pipeline
7. **Debugging Tools**: Built-in execution tracing and debugging

## Step-by-Step Integration

### Step 1: Install LangGraph
```bash
pip install langgraph
```

### Step 2: Current Architecture Analysis

**Current Manual Flow in `app.py`:**
```python
# Sequential execution
transcription_result = transcription_agent.process(transcript_text)
context_result = context_agent.analyze(transcription_result["cleaned_text"])
soap_notes = scribe_agent.generate_soap_notes(...)
concepts = concept_agent.extract_concepts(...)
icd_codes = icd_mapper_agent.map_to_icd10(concepts)
```

**Problems:**
- No parallelization (concept extraction could run parallel to SOAP generation)
- Manual error handling
- Hard-coded execution order
- No conditional logic

### Step 3: LangGraph Architecture Design

**New Graph-based Flow:**
```
START
  ↓
[Transcription Agent]
  ↓
[Context Agent]
  ↓
┌─[Scribe Agent]─────[Concept Agent]─┐
│                                    │
│   (parallel execution)             │
│                                    │
└─────────[ICD Mapper Agent]─────────┘
  ↓
[Feedback Agent] (conditional)
  ↓
[Formatter Agent]
  ↓
END
```

### Step 4: Implementation Plan

#### 4.1 Create State Schema
```python
class PipelineState(TypedDict):
    transcript_text: str
    transcription_result: Dict[str, Any]
    context_result: Dict[str, Any]
    soap_notes: Dict[str, str]
    concepts: List[Dict[str, Any]]
    icd_codes: List[Dict[str, Any]]
    errors: List[str]
    processing_metadata: Dict[str, Any]
```

#### 4.2 Define Agent Nodes
```python
def transcription_node(state: PipelineState) -> PipelineState:
    result = transcription_agent.process(state["transcript_text"])
    state["transcription_result"] = result
    return state

def context_node(state: PipelineState) -> PipelineState:
    result = context_agent.analyze(state["transcription_result"]["cleaned_text"])
    state["context_result"] = result
    return state
```

#### 4.3 Build Workflow Graph
```python
workflow = StateGraph(PipelineState)

# Add nodes
workflow.add_node("transcription", transcription_node)
workflow.add_node("context", context_node)
workflow.add_node("scribe", scribe_node)
workflow.add_node("concept", concept_node)
workflow.add_node("icd_mapping", icd_node)

# Define edges
workflow.set_entry_point("transcription")
workflow.add_edge("transcription", "context")
workflow.add_edge("context", "scribe")
workflow.add_edge("context", "concept")  # Parallel execution
workflow.add_edge(["scribe", "concept"], "icd_mapping")  # Wait for both
workflow.add_edge("icd_mapping", END)
```

### Step 5: Integration with Existing App

#### 5.1 Backward Compatibility
The new implementation maintains backward compatibility:
```python
class DocuScribeApp:
    def __init__(self):
        self.pipeline_mode = os.getenv("PIPELINE_MODE", "manual")
        
        if self.pipeline_mode == "langgraph":
            self.langgraph_pipeline = DocuScribeLangGraphPipeline()
        else:
            # Keep existing manual agents
            self.transcription_agent = TranscriptionAgent()
            # ... other agents
```

#### 5.2 Runtime Switching
Users can switch between pipeline modes:
```python
def process_transcript(self, transcript_text: str):
    if self.pipeline_mode == "langgraph":
        return self.process_transcript_langgraph(transcript_text)
    else:
        return self.process_transcript_manual(transcript_text)
```

### Step 6: Advanced Features

#### 6.1 Conditional Routing
```python
def should_run_feedback(state: PipelineState) -> str:
    # Route to feedback agent only if confidence is low
    avg_confidence = calculate_average_confidence(state)
    return "feedback" if avg_confidence < 0.7 else "formatter"

workflow.add_conditional_edges(
    "icd_mapping",
    should_run_feedback,
    {"feedback": "feedback_agent", "formatter": "formatter_agent"}
)
```

#### 6.2 Parallel Processing
```python
# Run SOAP generation and concept extraction in parallel
workflow.add_edge("context", "scribe")
workflow.add_edge("context", "concept")

# Wait for both to complete before ICD mapping
workflow.add_edge(["scribe", "concept"], "icd_mapping")
```

#### 6.3 Error Recovery
```python
def error_recovery_node(state: PipelineState) -> PipelineState:
    if state["errors"]:
        # Attempt to recover or provide fallback results
        state = attempt_recovery(state)
    return state
```

### Step 7: Testing the Integration

#### 7.1 Unit Tests
```python
def test_langgraph_pipeline():
    pipeline = DocuScribeLangGraphPipeline()
    
    test_transcript = "Doctor: How are you? Patient: I have a headache."
    result = pipeline.process_transcript(test_transcript)
    
    assert "soap_notes" in result
    assert "concepts" in result
    assert len(result["errors"]) == 0
```

#### 7.2 Performance Comparison
```python
def benchmark_pipelines():
    manual_time = time_manual_pipeline(test_transcript)
    langgraph_time = time_langgraph_pipeline(test_transcript)
    
    print(f"Manual: {manual_time:.2f}s")
    print(f"LangGraph: {langgraph_time:.2f}s")
    print(f"Speedup: {manual_time/langgraph_time:.2f}x")
```

### Step 8: Deployment Configuration

#### 8.1 Environment Variables
```bash
# .env file
PIPELINE_MODE=langgraph  # or "manual"
LANGGRAPH_ENABLE_PARALLEL=true
LANGGRAPH_MAX_RETRIES=3
```

#### 8.2 Streamlit Configuration
```python
# In sidebar
pipeline_mode = st.selectbox(
    "Pipeline Mode",
    ["manual", "langgraph"],
    help="Choose agent orchestration method"
)
```

## Migration Strategy

### Phase 1: Parallel Implementation (Week 1)
- Create LangGraph pipeline alongside existing manual pipeline
- Implement basic sequential flow
- Add runtime switching capability

### Phase 2: Feature Parity (Week 2)
- Add all existing features to LangGraph pipeline
- Implement error handling
- Add comprehensive testing

### Phase 3: Optimization (Week 3)
- Add parallel processing capabilities
- Implement conditional routing
- Performance optimization

### Phase 4: Full Migration (Week 4)
- Make LangGraph the default pipeline
- Maintain manual pipeline as fallback
- Update documentation

## Expected Benefits

### Performance Improvements:
- **25-40% faster processing** through parallel execution
- **Better error recovery** with automatic retries
- **Reduced memory usage** with optimized state management

### Developer Experience:
- **Easier debugging** with built-in tracing
- **Simpler agent addition** with graph-based configuration
- **Better testing** with isolated node testing

### Maintenance:
- **Cleaner code** with separation of concerns
- **Better scalability** for complex workflows
- **Improved monitoring** with built-in metrics

## Files to Modify

1. **`langgraph_pipeline.py`** - New LangGraph implementation
2. **`app_with_langgraph.py`** - Enhanced app with dual pipeline support
3. **`requirements.txt`** - Add langgraph dependency
4. **`.env.example`** - Add pipeline configuration options
5. **`README.md`** - Update with LangGraph information

## Next Steps

1. Install LangGraph: `pip install langgraph`
2. Test the pipeline: `python langgraph_pipeline.py`
3. Run enhanced app: `streamlit run app_with_langgraph.py`
4. Compare performance between manual and LangGraph modes
5. Gradually migrate features to LangGraph pipeline

This integration provides a smooth migration path while maintaining backward compatibility and allowing for easy comparison between the two approaches.
