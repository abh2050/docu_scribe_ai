# DocuScribe AI - Quick Start Guide

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Test the System**
   ```bash
   python test_system.py
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## 🔧 Configuration

### Required API Keys (at least one)
- **OpenAI**: Get from https://platform.openai.com/api-keys
- **Google**: Get from https://ai.google.dev/
- **Anthropic**: Get from https://console.anthropic.com/

### Environment Variables
Edit your `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-google-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
DEFAULT_LLM_PROVIDER=openai
DEFAULT_MODEL=gpt-4
```

## 📝 Using the System

1. **Load Example Transcript**
   - Use the sidebar to load pre-built examples
   - Or paste your own doctor-patient conversation

2. **Process the Transcript**
   - Click "🚀 Process Transcript"
   - Watch the agent pipeline execute
   - See real-time status updates

3. **Review Results**
   - Edit SOAP notes as needed
   - Validate extracted concepts
   - Review suggested ICD codes

4. **Export Results**
   - Download FHIR-compliant JSON
   - View human-readable summary
   - Submit feedback for improvements

## 🧪 Example Transcript Format

```
Doctor: Good morning, how are you feeling today?

Patient: I've been having headaches for the past week.

Doctor: Can you describe the headaches? When do they occur?

Patient: They're mostly in the mornings, and I rate them about 6/10 in pain.

Doctor: Let me check your blood pressure. *takes vitals* It's 140/90.

Doctor: I think we should adjust your medication and follow up in 2 weeks.
```

## 🔍 Key Features

- **Multi-Agent Processing**: Each step handled by specialized AI agents
- **Real-time SOAP Generation**: Automatic medical note creation
- **Concept Extraction**: Identifies medications, symptoms, vitals
- **ICD-10 Mapping**: Suggests appropriate diagnostic codes
- **Human-in-the-Loop**: Edit and improve results
- **FHIR Compliance**: EHR-ready output format

## 🛟 Troubleshooting

### "Import Error" when running
```bash
pip install -r requirements.txt
```

### "API Key not set" error
- Check your `.env` file has the correct API key
- Ensure the file is named `.env` (not `.env.txt`)
- Restart the application after setting keys

### "No concepts extracted"
- Check the transcript has medical content
- Ensure proper speaker labels (Doctor:, Patient:)
- Try with the provided example transcripts

### Performance Issues
- Use shorter transcripts for faster processing
- Consider using GPT-3.5-turbo instead of GPT-4
- Check your internet connection for API calls

## 📊 Output Formats

### SOAP Notes
```json
{
  "subjective": "Patient reports...",
  "objective": "Vital signs: BP 140/90...",
  "assessment": "Hypertension, uncontrolled...",
  "plan": "Increase medication, follow-up..."
}
```

### Medical Concepts
```json
[
  {
    "text": "lisinopril 10mg",
    "category": "medication_detailed",
    "confidence": 0.95
  }
]
```

### ICD-10 Codes
```json
[
  {
    "icd10_code": "I10",
    "description": "Essential hypertension",
    "confidence_score": 0.92
  }
]
```

## 🔗 Integration

### EHR Integration
- Use FHIR Bundle output for HL7 FHIR compatibility
- REST API endpoints available for system integration
- Webhook support for real-time processing

### Custom Workflows
- Modify agent prompts in each agent file
- Add custom medical vocabularies
- Extend ICD-10 mapping with additional codes

## 📞 Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Full API docs in `/docs`
- **Community**: Join our Discord for support

---

**Built for healthcare professionals to reduce documentation burden and improve patient care.**
