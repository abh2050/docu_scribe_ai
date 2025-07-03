#!/usr/bin/env python3
"""
Test script for the updated ICDMapperAgent
"""

import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.icd_mapper_agent import ICDMapperAgent

def test_icd_mapper():
    """Test the ICDMapperAgent with the new ICD-10 data"""
    print("Testing ICDMapperAgent with new ICD-10 data...")
    
    # Initialize the agent
    print("\n1. Initializing ICDMapperAgent...")
    agent = ICDMapperAgent()
    
    # Check if data was loaded
    print(f"   Loaded {len(agent.icd10_data)} ICD-10 codes")
    
    # Show some sample codes
    print("\n2. Sample ICD-10 codes loaded:")
    sample_codes = list(agent.icd10_data.items())[:10]
    for code, data in sample_codes:
        print(f"   {code}: {data['description']} ({data['category']})")
    
    # Test mapping with sample concepts
    print("\n3. Testing ICD-10 mapping...")
    sample_concepts = [
        {
            "text": "hypertension",
            "category": "conditions",
            "confidence": 0.9,
            "is_negated": False
        },
        {
            "text": "diabetes",
            "category": "conditions", 
            "confidence": 0.85,
            "is_negated": False
        },
        {
            "text": "headache",
            "category": "symptoms",
            "confidence": 0.8,
            "is_negated": False
        },
        {
            "text": "fever",
            "category": "symptoms",
            "confidence": 0.75,
            "is_negated": False
        }
    ]
    
    # Map concepts to ICD-10 codes
    icd_suggestions = agent.map_to_icd10(sample_concepts)
    
    print(f"   Found {len(icd_suggestions)} ICD-10 suggestions:")
    for suggestion in icd_suggestions:
        print(f"   - {suggestion['icd10_code']}: {suggestion['description']}")
        print(f"     Confidence: {suggestion['confidence_score']:.2f}, Source: {suggestion['source_concept']}")
        print(f"     Category: {suggestion['category']}")
    
    # Test code validation
    print("\n4. Testing code validation...")
    test_codes = ["I10", "E11.9", "R51", "INVALID"]
    for code in test_codes:
        validation = agent.validate_icd10_code(code)
        print(f"   {code}: Valid={validation['is_valid']}, Format={validation['format_correct']}, Exists={validation['exists_in_database']}")
        if validation['warnings']:
            print(f"     Warnings: {', '.join(validation['warnings'])}")
    
    print("\n✅ ICDMapperAgent test completed successfully!")

if __name__ == "__main__":
    test_icd_mapper()
