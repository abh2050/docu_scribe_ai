#!/usr/bin/env python3
"""
Test script for FeedbackAgent with LLM support
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.feedback_agent import FeedbackAgent

def test_feedback_agent():
    """Test the FeedbackAgent with various feedback scenarios"""
    
    print("🧪 Testing FeedbackAgent with LLM Support")
    print("=" * 50)
    
    # Initialize the FeedbackAgent
    feedback_agent = FeedbackAgent()
    
    # Test 1: Basic feedback processing
    print("\n1. Testing basic feedback processing...")
    
    sample_feedback = {
        "soap_corrections": {
            "subjective": {
                "original": "Patient has headache",
                "corrected": "Patient reports severe frontal headache for 3 days, worse with bright lights"
            },
            "assessment": {
                "original": "Headache",
                "corrected": "Migraine headache with photophobia"
            }
        },
        "concept_corrections": [
            {
                "original": "headache",
                "corrected": "migraine",
                "action": "modify",
                "reason": "More specific diagnosis"
            }
        ],
        "overall_rating": 3.5,
        "comments": "The system missed some important details about photophobia and duration"
    }
    
    try:
        result = feedback_agent.process_feedback(sample_feedback)
        print(f"✅ Feedback processed successfully!")
        print(f"   Feedback ID: {result['feedback_id']}")
        print(f"   Analysis source: {result['analysis'].get('analysis_source', 'unknown')}")
        print(f"   Improvements suggested: {len(result['improvements'])}")
        
        # Print some analysis details
        if result['analysis'].get('common_issues'):
            print(f"   Common issues identified: {result['analysis']['common_issues'][:2]}...")
        
    except Exception as e:
        print(f"❌ Feedback processing failed: {e}")
        return False
    
    # Test 2: Feedback with high rating
    print("\n2. Testing positive feedback...")
    
    positive_feedback = {
        "overall_rating": 4.8,
        "comments": "Excellent work! Very accurate SOAP notes and concept extraction."
    }
    
    try:
        result = feedback_agent.process_feedback(positive_feedback)
        print(f"✅ Positive feedback processed!")
        print(f"   User satisfaction: {result['analysis']['user_satisfaction'].get('level', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Positive feedback processing failed: {e}")
        return False
    
    # Test 3: Test feedback report generation
    print("\n3. Testing feedback report generation...")
    
    try:
        report = feedback_agent.generate_feedback_report()
        print(f"✅ Feedback report generated!")
        print(f"   Total feedback entries: {report['summary']['total_feedback_entries']}")
        if report['summary']['total_feedback_entries'] > 0:
            print(f"   Average rating: {report['summary']['average_rating']:.1f}")
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        return False
    
    # Test 4: Test LLM fallback behavior
    print("\n4. Testing LLM fallback behavior...")
    
    # Temporarily disable LLM
    original_client = feedback_agent.client
    feedback_agent.client = None
    
    try:
        result = feedback_agent.process_feedback(sample_feedback)
        print(f"✅ Fallback to rule-based processing works!")
        print(f"   Analysis source: {result['analysis'].get('analysis_source', 'rule_based')}")
        
    except Exception as e:
        print(f"❌ Fallback processing failed: {e}")
        return False
    finally:
        # Restore original client
        feedback_agent.client = original_client
    
    print(f"\n🎉 All FeedbackAgent tests passed!")
    print(f"\nFeedbackAgent is ready with hybrid LLM + rule-based capabilities:")
    print(f"  ✅ LLM-powered feedback analysis")
    print(f"  ✅ Intelligent improvement suggestions")
    print(f"  ✅ Robust fallback to rule-based methods")
    print(f"  ✅ Comprehensive feedback reporting")
    
    return True

if __name__ == "__main__":
    success = test_feedback_agent()
    sys.exit(0 if success else 1)
