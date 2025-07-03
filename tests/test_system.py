#!/usr/bin/env python3
"""
DocuScribe AI Test Script
Quick test to verify all agents work correctly
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_agents():
    """Test all agents with sample data"""
    print("🧪 Testing DocuScribe AI Agents")
    print("=" * 40)
    
    # Sample transcript
    sample_transcript = """
    Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?
    Patient: Good morning, Dr. Smith. I've been having some headaches lately, especially in the mornings.
    Doctor: I see. When did these headaches start? And have you been taking your blood pressure medication regularly?
    Patient: The headaches started about two weeks ago. And yes, I've been taking my lisinopril 10mg every morning as prescribed.
    Doctor: Good. Let me check your blood pressure today. Your blood pressure is 150 over 95, which is higher than we'd like to see.
    Patient: Is that bad? I've been trying to watch my salt intake like you suggested.
    Doctor: It's elevated, but we can manage this. The headaches could be related to the higher blood pressure. I think we need to increase your lisinopril to 20mg daily.
    """
    
    try:
        # Test Transcription Agent
        print("Testing Transcription Agent...")
        from agents.transcription_agent import TranscriptionAgent
        transcription_agent = TranscriptionAgent()
        transcription_result = transcription_agent.process(sample_transcript)
        print(f"✅ Transcription Agent: {transcription_result['word_count']} words processed")
        
        # Test Context Agent
        print("Testing Context Agent...")
        from agents.context_agent import ContextAgent
        context_agent = ContextAgent()
        context_result = context_agent.analyze(transcription_result['cleaned_text'])
        print(f"✅ Context Agent: {len(context_result['segments'])} segments identified")
        
        # Test Concept Agent
        print("Testing Concept Agent...")
        from agents.concept_agent import ConceptAgent
        concept_agent = ConceptAgent()
        concepts = concept_agent.extract_concepts(transcription_result['cleaned_text'])
        print(f"✅ Concept Agent: {len(concepts)} medical concepts extracted")
        
        # Test ICD Mapper Agent
        print("Testing ICD Mapper Agent...")
        from agents.icd_mapper_agent import ICDMapperAgent
        icd_agent = ICDMapperAgent()
        icd_codes = icd_agent.map_to_icd10(concepts)
        print(f"✅ ICD Mapper Agent: {len(icd_codes)} ICD codes suggested")
        
        # Test Scribe Agent (without LLM for basic test)
        print("Testing Scribe Agent...")
        from agents.scribe_agent import ScribeAgent
        scribe_agent = ScribeAgent()
        soap_notes = scribe_agent.generate_soap_fallback(
            transcription_result['cleaned_text'], 
            context_result['segments']
        )
        print(f"✅ Scribe Agent: SOAP notes generated")
        
        # Test Formatter Agent
        print("Testing Formatter Agent...")
        from agents.formatter_agent import FormatterAgent
        formatter_agent = FormatterAgent()
        formatted_output = formatter_agent.format_to_json({
            'soap_notes': soap_notes,
            'concepts': concepts,
            'icd_codes': icd_codes,
            'metadata': {'test': True}
        })
        print(f"✅ Formatter Agent: Output formatted successfully")
        
        # Test FHIR Formatter
        print("Testing FHIR Formatter...")
        from utils.fhir_formatter import FHIRFormatter
        fhir_formatter = FHIRFormatter()
        fhir_output = fhir_formatter.format_to_fhir({
            'soap_notes': soap_notes,
            'concepts': concepts,
            'icd_codes': icd_codes
        })
        print(f"✅ FHIR Formatter: FHIR bundle created")
        
        print("\n🎉 All tests passed! DocuScribe AI is ready to use.")
        print("\nTo start the application, run:")
        print("streamlit run app.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False

def main():
    """Main test function"""
    success = test_agents()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
