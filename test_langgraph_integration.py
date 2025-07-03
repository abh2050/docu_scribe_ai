#!/usr/bin/env python3
"""
Test script for LangGraph integration with DocuScribe AI
"""

import sys
import time
from typing import Dict, Any

def test_langgraph_availability():
    """Test if LangGraph is available"""
    try:
        import langgraph
        print("✅ LangGraph is available")
        return True
    except ImportError:
        print("❌ LangGraph is not installed")
        print("   Install with: pip install langgraph")
        return False

def test_manual_pipeline():
    """Test the existing manual pipeline"""
    print("\n🔄 Testing Manual Pipeline...")
    
    try:
        from agents.transcription_agent import TranscriptionAgent
        from agents.context_agent import ContextAgent
        from agents.scribe_agent import ScribeAgent
        from agents.concept_agent import ConceptAgent
        from agents.icd_mapper_agent import ICDMapperAgent
        
        # Initialize agents
        transcription_agent = TranscriptionAgent()
        context_agent = ContextAgent()
        scribe_agent = ScribeAgent()
        concept_agent = ConceptAgent()
        icd_mapper_agent = ICDMapperAgent()
        
        # Test transcript
        test_transcript = """
        Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?
        Patient: Good morning, Dr. Smith. I've been having some headaches lately, especially in the mornings.
        Doctor: When did these headaches start? Have you been taking your blood pressure medication regularly?
        Patient: The headaches started about two weeks ago. Yes, I've been taking my lisinopril 10mg every morning as prescribed.
        """
        
        print("   Processing transcript...")
        start_time = time.time()
        
        # Process through pipeline
        transcription_result = transcription_agent.process(test_transcript)
        context_result = context_agent.analyze(transcription_result["cleaned_text"])
        soap_notes = scribe_agent.generate_soap_notes(
            transcription_result["cleaned_text"], 
            context_result["segments"]
        )
        concepts = concept_agent.extract_concepts(transcription_result["cleaned_text"])
        icd_codes = icd_mapper_agent.map_to_icd10(concepts)
        
        processing_time = time.time() - start_time
        
        print(f"   ✅ Manual pipeline completed in {processing_time:.2f}s")
        print(f"   📊 Results: {len(concepts)} concepts, {len(icd_codes)} ICD codes")
        
        return {
            "processing_time": processing_time,
            "concepts_count": len(concepts),
            "icd_codes_count": len(icd_codes)
        }
        
    except Exception as e:
        print(f"   ❌ Manual pipeline failed: {str(e)}")
        return None

def test_langgraph_pipeline():
    """Test the LangGraph pipeline"""
    print("\n🔄 Testing LangGraph Pipeline...")
    
    try:
        from langgraph_pipeline import DocuScribeLangGraphPipeline
        
        # Initialize pipeline
        pipeline = DocuScribeLangGraphPipeline()
        
        # Test transcript
        test_transcript = """
        Doctor: Good morning, Mrs. Johnson. How have you been feeling since our last visit?
        Patient: Good morning, Dr. Smith. I've been having some headaches lately, especially in the mornings.
        Doctor: When did these headaches start? Have you been taking your blood pressure medication regularly?
        Patient: The headaches started about two weeks ago. Yes, I've been taking my lisinopril 10mg every morning as prescribed.
        """
        
        print("   Processing transcript...")
        start_time = time.time()
        
        # Process through LangGraph pipeline
        results = pipeline.process_transcript(test_transcript)
        
        processing_time = time.time() - start_time
        
        print(f"   ✅ LangGraph pipeline completed in {processing_time:.2f}s")
        print(f"   📊 Results: {len(results.get('concepts', []))} concepts, {len(results.get('icd_codes', []))} ICD codes")
        
        if results.get("errors"):
            print(f"   ⚠️  Errors: {results['errors']}")
        
        return {
            "processing_time": processing_time,
            "concepts_count": len(results.get('concepts', [])),
            "icd_codes_count": len(results.get('icd_codes', [])),
            "errors": results.get("errors", [])
        }
        
    except Exception as e:
        print(f"   ❌ LangGraph pipeline failed: {str(e)}")
        return None

def compare_pipelines(manual_results: Dict[str, Any], langgraph_results: Dict[str, Any]):
    """Compare the performance of both pipelines"""
    print("\n📊 Pipeline Comparison:")
    print("=" * 50)
    
    manual_time = manual_results["processing_time"]
    langgraph_time = langgraph_results["processing_time"]
    
    print(f"Manual Pipeline:    {manual_time:.2f}s")
    print(f"LangGraph Pipeline: {langgraph_time:.2f}s")
    
    if langgraph_time < manual_time:
        speedup = manual_time / langgraph_time
        print(f"🚀 LangGraph is {speedup:.2f}x faster")
    else:
        slowdown = langgraph_time / manual_time
        print(f"🐌 LangGraph is {slowdown:.2f}x slower")
    
    print(f"\nResults Comparison:")
    print(f"Manual concepts:    {manual_results['concepts_count']}")
    print(f"LangGraph concepts: {langgraph_results['concepts_count']}")
    print(f"Manual ICD codes:   {manual_results['icd_codes_count']}")
    print(f"LangGraph ICD codes:{langgraph_results['icd_codes_count']}")

def main():
    """Main test function"""
    print("🧪 DocuScribe AI - LangGraph Integration Test")
    print("=" * 50)
    
    # Test LangGraph availability
    langgraph_available = test_langgraph_availability()
    
    # Test manual pipeline
    manual_results = test_manual_pipeline()
    
    if not manual_results:
        print("❌ Manual pipeline test failed - cannot continue")
        return 1
    
    # Test LangGraph pipeline if available
    if langgraph_available:
        langgraph_results = test_langgraph_pipeline()
        
        if langgraph_results:
            compare_pipelines(manual_results, langgraph_results)
        else:
            print("❌ LangGraph pipeline test failed")
            return 1
    else:
        print("\n⚠️  Skipping LangGraph tests - not installed")
        print("   To test LangGraph integration:")
        print("   1. Install LangGraph: pip install langgraph")
        print("   2. Run this test again")
    
    print("\n✅ All available tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
