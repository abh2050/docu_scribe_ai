#!/usr/bin/env python3
"""
Evaluation Runner for DocuScribe AI
Automated evaluation of SOAP note generation, concept extraction, and ICD mapping
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from evaluation.llmops_evaluator import LLMOpsEvaluator
from agents.transcription_agent import TranscriptionAgent
from agents.context_agent import ContextAgent
from agents.scribe_agent import ScribeAgent
from agents.concept_agent import ConceptAgent
from agents.icd_mapper_agent import ICDMapperAgent
from agents.feedback_agent import FeedbackAgent
from agents.formatter_agent import FormatterAgent


def create_sample_reference_data():
    """Create sample reference data for evaluation"""
    reference_data = {
        "transcripts": [
            {
                "id": "sample_1",
                "transcript": """
                Doctor: Good morning, Mrs. Johnson. How are you feeling today?
                Patient: Hi doctor. I've been having this persistent headache for the past three days.
                Doctor: Can you describe the headache? Is it throbbing or constant?
                Patient: It's more of a constant ache, especially behind my eyes.
                Doctor: Any nausea or sensitivity to light?
                Patient: Yes, bright lights make it worse.
                Doctor: Have you taken any medication?
                Patient: Just some ibuprofen, but it doesn't help much.
                Doctor: Let me check your blood pressure. It's 150 over 95, which is elevated.
                """,
                "reference_soap": {
                    "subjective": "Patient reports persistent headache for 3 days, described as constant ache behind eyes. Associated with photophobia. Ibuprofen provides minimal relief.",
                    "objective": "Blood pressure 150/95 mmHg (elevated). Patient appears uncomfortable.",
                    "assessment": "Headache with hypertension. Possible tension headache vs. hypertensive headache.",
                    "plan": "1. Blood pressure monitoring 2. Consider antihypertensive medication 3. Follow-up in 1 week 4. Return if symptoms worsen"
                },
                "reference_concepts": [
                    {"concept": "headache", "category": "symptom"},
                    {"concept": "photophobia", "category": "symptom"},
                    {"concept": "hypertension", "category": "condition"},
                    {"concept": "ibuprofen", "category": "medication"}
                ],
                "reference_icd_codes": [
                    {"code": "R51.9", "description": "Headache, unspecified"},
                    {"code": "I10", "description": "Essential hypertension"}
                ]
            }
        ]
    }
    return reference_data


def run_pipeline(transcript, agents):
    """Run the full DocuScribe pipeline"""
    try:
        # Transcription (already provided)
        transcription = transcript

        # Context extraction
        context_result = agents['context'].process(transcription)
        segments = context_result["segments"] if isinstance(context_result, dict) and "segments" in context_result else []

        # SOAP note generation
        soap_notes = agents['scribe'].process((transcription, segments))

        # Concept extraction
        concepts = agents['concept'].process(transcription)

        # ICD mapping
        icd_codes = agents['icd'].process(concepts)

        # Format final output
        formatted_output = agents['formatter'].process({
            'soap_notes': soap_notes,
            'concepts': concepts,
            'icd_codes': icd_codes
        })

        return {
            'soap_notes': soap_notes,
            'concepts': concepts,
            'icd_codes': icd_codes,
            'formatted_output': formatted_output
        }
    except Exception as e:
        print(f"Error in pipeline: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Run DocuScribe AI Evaluation')
    parser.add_argument('--config', default='evaluation_config.json', help='Configuration file path')
    parser.add_argument('--output-dir', default='evaluation_results', help='Output directory for results')
    parser.add_argument('--reference-data', help='Path to reference data JSON file')
    parser.add_argument('--run-sample', action='store_true', help='Run with sample data')
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize evaluator
    evaluator = LLMOpsEvaluator()
    
    # Initialize agents
    agents = {
        'transcription': TranscriptionAgent(),
        'context': ContextAgent(),
        'scribe': ScribeAgent(),
        'concept': ConceptAgent(),
        'icd': ICDMapperAgent(),
        'feedback': FeedbackAgent(),
        'formatter': FormatterAgent()
    }
    
    # Load reference data
    if args.reference_data and Path(args.reference_data).exists():
        with open(args.reference_data, 'r') as f:
            reference_data = json.load(f)
    elif args.run_sample:
        reference_data = create_sample_reference_data()
        # Save sample data for future use
        sample_data_path = output_dir / 'sample_reference_data.json'
        with open(sample_data_path, 'w') as f:
            json.dump(reference_data, f, indent=2)
        print(f"Sample reference data saved to: {sample_data_path}")
    else:
        print("No reference data provided. Use --reference-data or --run-sample")
        return
    
    # Run evaluation
    results = []
    
    for item in reference_data['transcripts']:
        print(f"Processing transcript: {item['id']}")
        
        # Run pipeline
        pipeline_output = run_pipeline(item['transcript'], agents)
        
        if pipeline_output is None:
            print(f"Skipping {item['id']} due to pipeline error")
            continue
        
        # Evaluate SOAP notes
        soap_scores = evaluator.evaluate_soap_notes(
            generated=pipeline_output['soap_notes'],
            reference=item['reference_soap']
        )
        
        # Evaluate concepts
        concept_scores = evaluator.evaluate_concept_extraction(
            generated=pipeline_output['concepts'],
            reference=item['reference_concepts']
        )
        
        # Evaluate ICD codes
        icd_scores = evaluator.evaluate_icd_mapping(
            generated=pipeline_output['icd_codes'],
            reference=item['reference_icd_codes']
        )
        
        # Combine results
        result = {
            'transcript_id': item['id'],
            'timestamp': datetime.now().isoformat(),
            'soap_scores': soap_scores,
            'concept_scores': concept_scores,
            'icd_scores': icd_scores,
            'pipeline_output': pipeline_output
        }
        
        results.append(result)
        
        print(f"Completed evaluation for {item['id']}")
        print(f"SOAP BLEU: {soap_scores.get('bleu_score', 'N/A'):.3f}")
        print(f"Concept F1: {concept_scores.get('f1_score', 'N/A'):.3f}")
        print(f"ICD Accuracy: {icd_scores.get('accuracy', 'N/A'):.3f}")
        print("-" * 50)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f'evaluation_results_{timestamp}.json'
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Evaluation results saved to: {results_file}")
    
    # Generate summary report
    if results:
        summary = evaluator.generate_evaluation_report(results)
        summary_file = output_dir / f'evaluation_summary_{timestamp}.json'
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Evaluation summary saved to: {summary_file}")
        
        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        
        if 'soap_metrics' in summary:
            print(f"SOAP Notes - Avg BLEU: {summary['soap_metrics'].get('avg_bleu', 'N/A'):.3f}")
            print(f"SOAP Notes - Avg ROUGE-L: {summary['soap_metrics'].get('avg_rouge_l', 'N/A'):.3f}")
        
        if 'concept_metrics' in summary:
            print(f"Concepts - Avg F1: {summary['concept_metrics'].get('avg_f1', 'N/A'):.3f}")
            print(f"Concepts - Avg Precision: {summary['concept_metrics'].get('avg_precision', 'N/A'):.3f}")
        
        if 'icd_metrics' in summary:
            print(f"ICD Codes - Avg Accuracy: {summary['icd_metrics'].get('avg_accuracy', 'N/A'):.3f}")


if __name__ == '__main__':
    main()
