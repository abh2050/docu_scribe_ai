# DocuScribe AI - System Architecture (ASCII Diagram)

```
+-----------------------------------------------------------------------------------+
|                                   DocuScribe AI                                   |
|                                                                                   |
|  +-------------------+      +-------------------+      +----------------------+   |
|  |  Transcription    |----->|     Context       |----->|      Scribe          |   |
|  |     Agent         |      |      Agent        |      |      Agent           |   |
|  +-------------------+      +-------------------+      +----------------------+   |
|          |                        |                        |                      |
|          v                        v                        v                      |
|  +-------------------+      +-------------------+      +----------------------+   |
|  |   Concept Agent   |<-----|   Feedback Agent  |<-----|   ICD Mapper Agent   |   |
|  +-------------------+      +-------------------+      +----------------------+   |
|          |                        |                        |                      |
|          v                        v                        v                      |
|  +-------------------+      +-------------------+      +----------------------+   |
|  |   Formatter Agent |----->|   FHIR Formatter  |----->|   Output (FHIR/JSON) |   |
|  +-------------------+      +-------------------+      +----------------------+   |
|                                                                                   |
|  +-------------------+                                                           |
|  |   LLMOps &        |                                                           |
|  |   Evaluation      |<--------------------------------------------------------+  |
|  |   Pipeline        |   (Monitors, scores, and logs all agent outputs)         |  |
|  +-------------------+---------------------------------------------------------+  |
|                                                                                   |
|  +-------------------+                                                           |
|  |   Streamlit UI    |<--------------------------------------------------------+  |
|  +-------------------+   (User input, review, feedback, dashboard, export)      |  |
+-----------------------------------------------------------------------------------+
```

**Legend:**
- Each box is an agent/module.
- Arrows show data flow and dependencies.
- LLMOps/Evaluation and UI monitor and interact with all stages.

**Key Components:**
- Transcription Agent: Converts audio/text to transcript.
- Context Agent: Segments and classifies transcript.
- Scribe Agent: Generates SOAP notes.
- Concept Agent: Extracts clinical concepts.
- ICD Mapper Agent: Suggests ICD-10 codes.
- Feedback Agent: Handles human-in-the-loop feedback.
- Formatter Agent: Prepares output for FHIR/EHR.
- FHIR Formatter: Converts to FHIR-like JSON.
- LLMOps/Evaluation: Monitors, scores, and logs outputs.
- Streamlit UI: User interface for review, feedback, and export.
