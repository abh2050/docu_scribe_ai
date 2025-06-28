![](https://github.com/abh2050/docu_scribe_ai/blob/main/assets/ChatGPT%20Image%20Jun%2028%2C%202025%2C%2003_27_16%20PM.png)
# 🩺 DocuScribe AI - Agentic Ambient Scribing System

DocuScribe AI is an intelligent, agentic system that transforms clinical conversations into structured medical documentation. Using advanced LLM orchestration and medical knowledge systems, it generates SOAP notes, extracts medical concepts, and suggests ICD-10 codes while maintaining human oversight through an intuitive feedback loop.

## Presentation
https://abh2050.github.io/docu_scribe_ai/

## 🎯 Project Overview

**Problem**: Clinicians spend excessive time on documentation, leading to burnout and reduced patient interaction time.

**Solution**: An AI-powered ambient scribing system that:
- Generates SOAP notes in real-time
- Extracts key clinical concepts (medications, vitals, symptoms)
- Suggests diagnostic codes (ICD-10) based on extracted terms
- Allows user feedback and corrections (human-in-the-loop)
- Stores notes in structured format (FHIR-like JSON) for EHR integration

## 🏗️ Architecture

The system follows an agentic architecture with specialized agents for different tasks:

```
┌────────────┐
│ Start Node │
└─────┬──────┘
      │
┌─────▼─────┐    ┌──────────────┐    ┌─────────────┐
│Transcription│ → │Context Agent │ → │Scribe Agent │
│   Agent     │   │   (SOAP)     │   │(LLM SOAP)   │
└─────────────┘   └──────────────┘   └─────┬───────┘
                                           │
┌─────────────┐    ┌──────────────┐       │
│ICD Mapper   │ ← │Concept Agent │ ←─────┘
│   Agent     │   │(NER + UMLS)  │
└─────┬───────┘   └──────────────┘
      │
┌─────▼─────┐    ┌──────────────┐    ┌─────────────┐
│Feedback   │ → │ Formatter    │ → │Final Output │
│  Agent    │   │    Agent     │   │(FHIR/JSON)  │
└───────────┘   └──────────────┘   └─────────────┘
```

## 🚀 Features

### Core Capabilities
- **Multi-Agent Architecture**: Specialized agents for transcription, context analysis, medical scribing, concept extraction, ICD mapping, feedback processing, and output formatting
- **SOAP Note Generation**: Automated generation of Subjective, Objective, Assessment, and Plan sections
- **Medical Concept Extraction**: NLP-powered extraction of medications, symptoms, vitals, conditions, and procedures
- **ICD-10 Code Mapping**: Intelligent mapping of clinical concepts to appropriate diagnostic codes
- **Human-in-the-Loop**: Interactive feedback system for corrections and improvements
- **Multiple Output Formats**: FHIR, HL7, JSON, XML, and human-readable text formats

### Advanced Features
- **Confidence Scoring**: AI confidence levels for all extracted information
- **Real-time Processing**: Live processing with visual agent status indicators  
- **Validation & Quality Checks**: Automated validation of generated content
- **Metrics Dashboard**: Processing time, accuracy scores, and improvement tracking
- **EHR Integration Ready**: FHIR-compliant output for seamless EHR integration

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Frontend** | Streamlit (Interactive Web UI) |
| **Backend** | Python + FastAPI |
| **LLM Integration** | OpenAI GPT-4, Google Gemini, Anthropic Claude |
| **Agent Framework** | LangChain + LangGraph |
| **Medical Knowledge** | UMLS API + Custom Medical Vocabularies |
| **Code Mapping** | ICD-10 CSV + Fuzzy String Matching |
| **Output Formats** | FHIR R4, HL7, JSON Schema |
| **NLP** | spaCy, Custom Medical NER |

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- API keys for chosen LLM provider(s)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/abh2050/docu_scribe_ai.git
cd docu_sciibe_ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
streamlit run app.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Model Configuration
DEFAULT_LLM_PROVIDER=openai  # openai, google, anthropic
DEFAULT_MODEL=gpt-4

# Optional: UMLS Configuration
UMLS_API_KEY=your_umls_api_key_here

# App Configuration
DEBUG=True
LOG_LEVEL=INFO
```

### Supported LLM Providers
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Google**: Gemini Pro
- **Anthropic**: Claude-3-sonnet

## 📋 Usage

### Basic Workflow

1. **Start the Application**
   ```bash
   streamlit run app.py
   ```

2. **Input Clinical Transcript**
   - Paste doctor-patient conversation transcript
   - Use provided example transcripts for testing

3. **Process Through Agent Pipeline**
   - Watch real-time agent status indicators
   - See processing progress through each stage

4. **Review & Edit Results**
   - Review generated SOAP notes
   - Edit any sections as needed
   - Validate extracted concepts and ICD codes

5. **Export Results**
   - Download FHIR-compliant JSON
   - View metrics and confidence scores
   - Submit feedback for system improvement

### Example Input

```
Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?

Patient: Good morning, Dr. Smith. I've been having some headaches lately, especially in the mornings.

Doctor: When did these headaches start? Have you been taking your blood pressure medication regularly?

Patient: The headaches started about two weeks ago. Yes, I've been taking my lisinopril 10mg every morning as prescribed.

Doctor: Let me check your blood pressure. *takes blood pressure* Your blood pressure is 150 over 95, which is elevated.

...
```

### Example Output

```json
{
  "soap_notes": {
    "subjective": "Patient reports morning headaches starting 2 weeks ago. Taking lisinopril 10mg daily as prescribed.",
    "objective": "Blood pressure: 150/95 mmHg (elevated)",
    "assessment": "Hypertension, inadequately controlled. Morning headaches likely related to elevated BP.",
    "plan": "Increase lisinopril to 20mg daily. Order kidney function labs. Follow-up in 4 weeks."
  },
  "extracted_concepts": [
    {
      "text": "lisinopril 10mg",
      "category": "medication_detailed",
      "confidence": 0.95
    },
    {
      "text": "150/95",
      "category": "vital_measurement",
      "confidence": 0.98
    }
  ],
  "icd_codes": [
    {
      "icd10_code": "I10",
      "description": "Essential (primary) hypertension",
      "confidence_score": 0.92
    }
  ]
}
```

## 🧪 Testing

### Run with Example Data

The system includes example clinical transcripts:

1. **Hypertension Follow-up**: `data/example_transcripts/hypertension_followup.txt`
2. **Diabetes Management**: `data/example_transcripts/diabetes_management.txt`

Load these examples through the sidebar in the Streamlit interface.

### Agent Testing

Each agent can be tested independently:

```python
from agents.scribe_agent import ScribeAgent

scribe = ScribeAgent()
soap_notes = scribe.generate_soap_notes(transcript, segments)
```

## 📊 Performance Metrics

The system tracks several key metrics:

- **Processing Time**: Total time for complete pipeline
- **Confidence Scores**: AI confidence in extracted information
- **Completeness**: Percentage of SOAP sections populated
- **Accuracy**: Based on user feedback and corrections
- **Concept Extraction Rate**: Number of medical concepts identified

## 🔄 Human-in-the-Loop Feedback

### Feedback Types
- **SOAP Note Corrections**: Edit generated content
- **Concept Validation**: Add/remove/modify extracted concepts
- **ICD Code Review**: Validate suggested diagnostic codes
- **Overall Rating**: 1-5 star system for quality assessment

### Learning & Improvement
- System learns from user corrections
- Adjusts confidence thresholds based on feedback
- Tracks improvement trends over time
- Generates recommendations for system enhancement

## 🏥 EHR Integration

### FHIR Compliance
- Full FHIR R4 compatibility
- Patient, Practitioner, Encounter resources
- Observation resources for vitals and measurements
- Condition resources for diagnoses
- MedicationStatement resources for prescriptions

### Integration Points
- RESTful API endpoints for EHR systems
- Standard HL7 FHIR Bundle format
- Webhook support for real-time integration
- Audit trails and logging for compliance

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
```bash
# Using Docker
docker build -t docuscribe-ai .
docker run -p 8501:8501 docuscribe-ai

```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Medical Terminology**: UMLS (Unified Medical Language System)
- **ICD-10 Codes**: WHO International Classification of Diseases
- **FHIR Standards**: HL7 FHIR Implementation Guide
- **LLM Providers**: OpenAI, Google, Anthropic for powerful language models

## 🔮 Roadmap

### Version 2.0
- [ ] Voice transcription integration (Whisper)
- [ ] Real-time streaming processing
- [ ] Multi-language support
- [ ] Advanced clinical decision support
- [ ] Integration with major EHR systems

### Version 3.0
- [ ] AI-powered clinical insights
- [ ] Predictive health analytics
- [ ] Population health metrics
- [ ] Advanced privacy controls (differential privacy)
