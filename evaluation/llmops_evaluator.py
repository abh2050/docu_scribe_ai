from typing import Dict, Any, List, Optional, Tuple
import json
import logging
import time
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from nltk.translate.bleu_score import sentence_bleu, corpus_bleu
try:
    from rouge_score import rouge_scorer
    ROUGE_AVAILABLE = True
except ImportError:
    print("Warning: rouge-score not available. ROUGE metrics will be skipped.")
    ROUGE_AVAILABLE = False
import openai
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class EvaluationResult:
    """Data class for evaluation results"""
    metric_name: str
    score: float
    details: Dict[str, Any]
    timestamp: datetime
    model_version: str
    sample_size: int

class LLMOpsEvaluator:
    """Comprehensive evaluation pipeline for DocuScribe AI LLM performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if ROUGE_AVAILABLE:
            self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        else:
            self.rouge_scorer = None
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.evaluation_history = []
        
    def evaluate_soap_generation(self, 
                                generated_soap: Dict[str, str], 
                                reference_soap: Dict[str, str],
                                transcript: str = "") -> Dict[str, EvaluationResult]:
        """
        Comprehensive evaluation of SOAP note generation
        
        Args:
            generated_soap: AI-generated SOAP notes
            reference_soap: Ground truth SOAP notes
            transcript: Original transcript for context
            
        Returns:
            Dictionary of evaluation results
        """
        results = {}
        
        # BLEU Score Evaluation
        bleu_result = self.calculate_bleu_scores(generated_soap, reference_soap)
        results["bleu"] = bleu_result
        
        # ROUGE Score Evaluation
        rouge_result = self.calculate_rouge_scores(generated_soap, reference_soap)
        results["rouge"] = rouge_result
        
        # Clinical Accuracy Evaluation (LLM-as-a-Judge)
        clinical_result = self.evaluate_clinical_accuracy(generated_soap, reference_soap, transcript)
        results["clinical_accuracy"] = clinical_result
        
        # Completeness Evaluation
        completeness_result = self.evaluate_completeness(generated_soap, reference_soap)
        results["completeness"] = completeness_result
        
        # Medical Terminology Accuracy
        medical_term_result = self.evaluate_medical_terminology(generated_soap, reference_soap)
        results["medical_terminology"] = medical_term_result
        
        # Structure and Format Evaluation
        structure_result = self.evaluate_structure_format(generated_soap, reference_soap)
        results["structure_format"] = structure_result
        
        return results
    
    def calculate_bleu_scores(self, 
                            generated_soap: Dict[str, str], 
                            reference_soap: Dict[str, str]) -> EvaluationResult:
        """Calculate BLEU scores for SOAP sections, skipping empty sections and ensuring lists match."""
        bleu_scores = {}
        all_generated = []
        all_reference = []
        for section in ["subjective", "objective", "assessment", "plan"]:
            gen = generated_soap.get(section, "").strip()
            ref = reference_soap.get(section, "").strip()
            if gen and ref:
                generated_tokens = gen.lower().split()
                reference_tokens = [ref.lower().split()]
                bleu_4 = sentence_bleu(reference_tokens, generated_tokens, weights=(0.25, 0.25, 0.25, 0.25))
                bleu_scores[section] = bleu_4
                all_generated.append(generated_tokens)
                all_reference.append(reference_tokens[0])
        # Only compute corpus BLEU if lists are non-empty and same length
        if all_generated and all_reference and len(all_generated) == len(all_reference):
            corpus_bleu_score = corpus_bleu([[ref] for ref in all_reference], all_generated)
        else:
            corpus_bleu_score = 0.0
        average_bleu = np.mean(list(bleu_scores.values())) if bleu_scores else 0.0
        details = {
            "section_scores": bleu_scores,
            "corpus_bleu": corpus_bleu_score,
            "average_bleu": average_bleu,
            "sections_evaluated": len(bleu_scores)
        }
        return EvaluationResult(
            metric_name="bleu",
            score=average_bleu,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(bleu_scores)
        )
    
    def calculate_rouge_scores(self, 
                             generated_soap: Dict[str, str], 
                             reference_soap: Dict[str, str]) -> EvaluationResult:
        """Calculate ROUGE scores for SOAP sections"""
        
        if not ROUGE_AVAILABLE or not self.rouge_scorer:
            return EvaluationResult(
                metric_name="rouge",
                score=0.0,
                details={"error": "ROUGE scorer not available"},
                timestamp=datetime.now(),
                model_version="current",
                sample_size=0
            )
        
        rouge_scores = {}
        all_scores = {"rouge1": [], "rouge2": [], "rougeL": []}
        
        for section in ["subjective", "objective", "assessment", "plan"]:
            if section in generated_soap and section in reference_soap:
                try:
                    scores = self.rouge_scorer.score(
                        reference_soap[section],
                        generated_soap[section]
                    )
                    
                    rouge_scores[section] = {
                        "rouge1": scores["rouge1"].fmeasure,
                        "rouge2": scores["rouge2"].fmeasure,
                        "rougeL": scores["rougeL"].fmeasure
                    }
                    
                    for metric in all_scores:
                        all_scores[metric].append(scores[metric].fmeasure)
                        
                except Exception as e:
                    self.logger.warning(f"Error calculating ROUGE for {section}: {e}")
        
        # Calculate averages
        average_scores = {}
        for metric in all_scores:
            if all_scores[metric]:
                average_scores[metric] = np.mean(all_scores[metric])
            else:
                average_scores[metric] = 0.0
        
        overall_score = np.mean(list(average_scores.values()))
        
        details = {
            "section_scores": rouge_scores,
            "average_scores": average_scores,
            "overall_rouge": overall_score
        }
        
        return EvaluationResult(
            metric_name="rouge",
            score=overall_score,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(rouge_scores)
        )
    
    def evaluate_clinical_accuracy(self, 
                                 generated_soap: Dict[str, str], 
                                 reference_soap: Dict[str, str],
                                 transcript: str = "") -> EvaluationResult:
        """Use LLM-as-a-Judge to evaluate clinical accuracy"""
        
        judge_prompt = """You are an expert clinical documentation reviewer. Your task is to evaluate the accuracy and quality of AI-generated SOAP notes compared to reference SOAP notes.

Please evaluate the following dimensions on a scale of 1-10:
1. Clinical Accuracy: How accurately does the generated note capture the clinical information?
2. Medical Terminology: How appropriate and accurate is the medical terminology used?
3. Completeness: How complete is the generated note compared to the reference?
4. Consistency: How consistent is the information across SOAP sections?
5. Professional Quality: How well does it meet professional medical documentation standards?

Generated SOAP Note:
{generated_soap}

Reference SOAP Note:
{reference_soap}

Original Transcript (for context):
{transcript}

Please provide your evaluation in this JSON format:
{{
  "clinical_accuracy": <score 1-10>,
  "medical_terminology": <score 1-10>,
  "completeness": <score 1-10>,
  "consistency": <score 1-10>,
  "professional_quality": <score 1-10>,
  "overall_score": <average of above scores>,
  "reasoning": "Brief explanation of the scores",
  "strengths": ["list", "of", "strengths"],
  "areas_for_improvement": ["list", "of", "areas", "to", "improve"]
}}
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert medical documentation reviewer."},
                    {"role": "user", "content": judge_prompt.format(
                        generated_soap=json.dumps(generated_soap, indent=2),
                        reference_soap=json.dumps(reference_soap, indent=2),
                        transcript=transcript[:1000] + "..." if len(transcript) > 1000 else transcript
                    )}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            judge_result = json.loads(response.choices[0].message.content)
            overall_score = judge_result.get("overall_score", 0) / 10.0  # Normalize to 0-1
            
        except Exception as e:
            self.logger.error(f"Error in LLM-as-a-Judge evaluation: {e}")
            judge_result = {"error": str(e)}
            overall_score = 0.0
        
        return EvaluationResult(
            metric_name="clinical_accuracy",
            score=overall_score,
            details=judge_result,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=1
        )
    
    def evaluate_completeness(self, 
                            generated_soap: Dict[str, str], 
                            reference_soap: Dict[str, str]) -> EvaluationResult:
        """Evaluate completeness of SOAP sections"""
        
        required_sections = ["subjective", "objective", "assessment", "plan"]
        
        completeness_scores = {}
        for section in required_sections:
            gen_present = section in generated_soap and len(generated_soap[section].strip()) > 0
            ref_present = section in reference_soap and len(reference_soap[section].strip()) > 0
            
            if ref_present:
                if gen_present:
                    # Calculate length ratio as a proxy for completeness
                    gen_length = len(generated_soap[section].split())
                    ref_length = len(reference_soap[section].split())
                    length_ratio = min(gen_length / ref_length, 1.0) if ref_length > 0 else 0.0
                    completeness_scores[section] = length_ratio
                else:
                    completeness_scores[section] = 0.0
            elif gen_present:
                # Generated section when reference doesn't have it (could be positive)
                completeness_scores[section] = 0.5
        
        overall_completeness = np.mean(list(completeness_scores.values())) if completeness_scores else 0.0
        
        details = {
            "section_completeness": completeness_scores,
            "sections_present_generated": len([s for s in required_sections if s in generated_soap]),
            "sections_present_reference": len([s for s in required_sections if s in reference_soap]),
            "overall_completeness": overall_completeness
        }
        
        return EvaluationResult(
            metric_name="completeness",
            score=overall_completeness,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(required_sections)
        )
    
    def evaluate_medical_terminology(self, 
                                   generated_soap: Dict[str, str], 
                                   reference_soap: Dict[str, str]) -> EvaluationResult:
        """Evaluate accuracy of medical terminology usage"""
        
        # Common medical terms and their variations
        medical_terms_db = {
            "hypertension": ["high blood pressure", "htn", "elevated bp"],
            "diabetes": ["diabetes mellitus", "dm", "blood sugar", "glucose"],
            "medication": ["drug", "prescription", "medicine", "pharmaceutical"],
            "symptoms": ["complaints", "manifestations", "presentations"],
            "examination": ["exam", "assessment", "evaluation", "inspection"]
        }
        
        terminology_matches = {}
        
        for section in generated_soap:
            if section in reference_soap:
                gen_text = generated_soap[section].lower()
                ref_text = reference_soap[section].lower()
                
                matches = 0
                total_medical_terms = 0
                
                for base_term, variations in medical_terms_db.items():
                    all_terms = [base_term] + variations
                    
                    ref_has_term = any(term in ref_text for term in all_terms)
                    gen_has_term = any(term in gen_text for term in all_terms)
                    
                    if ref_has_term:
                        total_medical_terms += 1
                        if gen_has_term:
                            matches += 1
                
                if total_medical_terms > 0:
                    terminology_matches[section] = matches / total_medical_terms
                else:
                    terminology_matches[section] = 1.0  # No medical terms to match
        
        overall_accuracy = np.mean(list(terminology_matches.values())) if terminology_matches else 0.0
        
        details = {
            "section_accuracy": terminology_matches,
            "overall_accuracy": overall_accuracy,
            "medical_terms_evaluated": len(medical_terms_db)
        }
        
        return EvaluationResult(
            metric_name="medical_terminology",
            score=overall_accuracy,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(terminology_matches)
        )
    
    def evaluate_structure_format(self, 
                                generated_soap: Dict[str, str], 
                                reference_soap: Dict[str, str]) -> EvaluationResult:
        """Evaluate structure and formatting of SOAP notes"""
        
        structure_scores = {}
        
        # Check if all required sections are present
        required_sections = ["subjective", "objective", "assessment", "plan"]
        sections_present = sum(1 for s in required_sections if s in generated_soap)
        structure_scores["sections_present"] = sections_present / len(required_sections)
        
        # Check section length appropriateness
        section_lengths = {}
        for section in generated_soap:
            if generated_soap[section]:
                word_count = len(generated_soap[section].split())
                # Ideal word counts for each section (rough guidelines)
                ideal_lengths = {
                    "subjective": (20, 100),
                    "objective": (15, 80),
                    "assessment": (10, 60),
                    "plan": (15, 80)
                }
                
                if section in ideal_lengths:
                    min_len, max_len = ideal_lengths[section]
                    if min_len <= word_count <= max_len:
                        section_lengths[section] = 1.0
                    elif word_count < min_len:
                        section_lengths[section] = word_count / min_len
                    else:
                        section_lengths[section] = max_len / word_count
                else:
                    section_lengths[section] = 1.0
        
        structure_scores["length_appropriateness"] = np.mean(list(section_lengths.values())) if section_lengths else 0.0
        
        # Check for professional formatting (proper capitalization, punctuation)
        formatting_scores = {}
        for section, content in generated_soap.items():
            score = 0.0
            if content:
                # Check capitalization
                if content[0].isupper():
                    score += 0.3
                # Check punctuation
                if content.strip().endswith('.'):
                    score += 0.3
                # Check for reasonable sentence structure
                sentences = content.split('.')
                if len(sentences) >= 2:
                    score += 0.4
                
                formatting_scores[section] = score
        
        structure_scores["formatting"] = np.mean(list(formatting_scores.values())) if formatting_scores else 0.0
        
        overall_structure = np.mean(list(structure_scores.values()))
        
        details = {
            "structure_breakdown": structure_scores,
            "section_lengths": section_lengths,
            "formatting_scores": formatting_scores,
            "overall_structure": overall_structure
        }
        
        return EvaluationResult(
            metric_name="structure_format",
            score=overall_structure,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(generated_soap)
        )
    
    def evaluate_concept_extraction(self, 
                                  extracted_concepts: List[Dict[str, Any]], 
                                  reference_concepts: List[Dict[str, Any]]) -> Dict[str, EvaluationResult]:
        """Evaluate concept extraction performance"""
        
        results = {}
        
        # Precision, Recall, F1 for concept extraction
        extraction_metrics = self.calculate_extraction_metrics(extracted_concepts, reference_concepts)
        results["extraction_metrics"] = extraction_metrics
        
        # Category-wise accuracy
        category_metrics = self.calculate_category_metrics(extracted_concepts, reference_concepts)
        results["category_metrics"] = category_metrics
        
        return results
    
    def calculate_extraction_metrics(self, 
                                   extracted: List[Dict[str, Any]], 
                                   reference: List[Dict[str, Any]]) -> EvaluationResult:
        """Calculate precision, recall, and F1 for concept extraction"""
        
        # Extract concept texts for comparison
        extracted_texts = set(concept.get("text", "").lower() for concept in extracted)
        reference_texts = set(concept.get("text", "").lower() for concept in reference)
        
        # Calculate metrics
        true_positives = len(extracted_texts.intersection(reference_texts))
        false_positives = len(extracted_texts - reference_texts)
        false_negatives = len(reference_texts - extracted_texts)
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0.0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        details = {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "extracted_count": len(extracted),
            "reference_count": len(reference)
        }
        
        return EvaluationResult(
            metric_name="extraction_metrics",
            score=f1_score,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(reference)
        )
    
    def calculate_category_metrics(self, 
                                 extracted: List[Dict[str, Any]], 
                                 reference: List[Dict[str, Any]]) -> EvaluationResult:
        """Calculate metrics by concept category"""
        
        categories = set()
        for concept in extracted + reference:
            categories.add(concept.get("category", "unknown"))
        
        category_results = {}
        
        for category in categories:
            extracted_cat = [c for c in extracted if c.get("category") == category]
            reference_cat = [c for c in reference if c.get("category") == category]
            
            extracted_texts = set(c.get("text", "").lower() for c in extracted_cat)
            reference_texts = set(c.get("text", "").lower() for c in reference_cat)
            
            tp = len(extracted_texts.intersection(reference_texts))
            fp = len(extracted_texts - reference_texts)
            fn = len(reference_texts - extracted_texts)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            category_results[category] = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "extracted_count": len(extracted_cat),
                "reference_count": len(reference_cat)
            }
        
        overall_f1 = np.mean([metrics["f1_score"] for metrics in category_results.values()])
        
        details = {
            "category_breakdown": category_results,
            "overall_f1": overall_f1,
            "categories_evaluated": len(categories)
        }
        
        return EvaluationResult(
            metric_name="category_metrics",
            score=overall_f1,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(categories)
        )
    
    def evaluate_icd_mapping(self, 
                           predicted_codes: List[Dict[str, Any]], 
                           reference_codes: List[Dict[str, Any]]) -> EvaluationResult:
        """Evaluate ICD-10 code mapping accuracy"""
        
        predicted_icd = set(code.get("icd10_code", "") for code in predicted_codes)
        reference_icd = set(code.get("icd10_code", "") for code in reference_codes)
        
        # Calculate exact match metrics
        exact_matches = len(predicted_icd.intersection(reference_icd))
        precision = exact_matches / len(predicted_icd) if predicted_icd else 0.0
        recall = exact_matches / len(reference_icd) if reference_icd else 0.0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        # Calculate top-k accuracy (if confidence scores available)
        top_k_accuracy = self.calculate_top_k_icd_accuracy(predicted_codes, reference_codes)
        
        details = {
            "exact_match_precision": precision,
            "exact_match_recall": recall,
            "exact_match_f1": f1_score,
            "top_k_accuracy": top_k_accuracy,
            "predicted_codes_count": len(predicted_codes),
            "reference_codes_count": len(reference_codes),
            "exact_matches": exact_matches
        }
        
        return EvaluationResult(
            metric_name="icd_mapping",
            score=f1_score,
            details=details,
            timestamp=datetime.now(),
            model_version="current",
            sample_size=len(reference_codes)
        )
    
    def calculate_top_k_icd_accuracy(self, 
                                   predicted: List[Dict[str, Any]], 
                                   reference: List[Dict[str, Any]], 
                                   k_values: List[int] = [1, 3, 5]) -> Dict[str, float]:
        """Calculate top-k accuracy for ICD code predictions"""
        
        if not reference:
            return {f"top_{k}": 0.0 for k in k_values}
        
        # Sort predicted codes by confidence
        predicted_sorted = sorted(predicted, 
                                key=lambda x: x.get("confidence_score", 0), 
                                reverse=True)
        
        reference_codes = set(code.get("icd10_code", "") for code in reference)
        
        top_k_accuracies = {}
        
        for k in k_values:
            top_k_predicted = set(code.get("icd10_code", "") 
                                for code in predicted_sorted[:k])
            
            hits = len(top_k_predicted.intersection(reference_codes))
            accuracy = hits / len(reference_codes) if reference_codes else 0.0
            top_k_accuracies[f"top_{k}"] = accuracy
        
        return top_k_accuracies
    
    # Simplified evaluation methods for run_evaluation.py compatibility
    
    def evaluate_soap_notes(self, generated: Dict[str, str], reference: Dict[str, str]) -> Dict[str, float]:
        """Simplified SOAP note evaluation"""
        try:
            # Calculate BLEU scores
            bleu_result = self.calculate_bleu_scores(generated, reference)
            
            # Calculate ROUGE scores
            rouge_result = self.calculate_rouge_scores(generated, reference)
            
            return {
                'bleu_score': bleu_result.score,
                'rouge_score': rouge_result.score,
                'details': {
                    'bleu_details': bleu_result.details,
                    'rouge_details': rouge_result.details
                }
            }
        except Exception as e:
            self.logger.error(f"Error in SOAP evaluation: {e}")
            return {'bleu_score': 0.0, 'rouge_score': 0.0, 'error': str(e)}
    
    def evaluate_concept_extraction(self, generated: List[Dict], reference: List[Dict]) -> Dict[str, float]:
        """Simplified concept extraction evaluation"""
        try:
            # Convert to sets for comparison
            generated_concepts = {(c.get('concept', ''), c.get('category', '')) for c in generated}
            reference_concepts = {(c.get('concept', ''), c.get('category', '')) for c in reference}
            
            # Calculate metrics
            tp = len(generated_concepts.intersection(reference_concepts))
            fp = len(generated_concepts - reference_concepts)
            fn = len(reference_concepts - generated_concepts)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            
            return {
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn
            }
        except Exception as e:
            self.logger.error(f"Error in concept evaluation: {e}")
            return {'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0, 'error': str(e)}
    
    def evaluate_icd_mapping(self, generated: List[Dict], reference: List[Dict]) -> Dict[str, float]:
        """Simplified ICD mapping evaluation"""
        try:
            # Extract codes
            generated_codes = {c.get('code', '') for c in generated}
            reference_codes = {c.get('code', '') for c in reference}
            
            # Calculate metrics
            tp = len(generated_codes.intersection(reference_codes))
            fp = len(generated_codes - reference_codes)
            fn = len(reference_codes - generated_codes)
            
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
            accuracy = tp / len(reference_codes) if len(reference_codes) > 0 else 0.0
            
            return {
                'accuracy': accuracy,
                'precision': precision,
                'recall': recall,
                'f1_score': f1_score,
                'true_positives': tp,
                'false_positives': fp,
                'false_negatives': fn
            }
        except Exception as e:
            self.logger.error(f"Error in ICD evaluation: {e}")
            return {'accuracy': 0.0, 'precision': 0.0, 'recall': 0.0, 'f1_score': 0.0, 'error': str(e)}
    
    def generate_evaluation_report(self, results: List[Dict]) -> Dict[str, Any]:
        """Generate summary report from evaluation results"""
        if not results:
            return {'error': 'No results to summarize'}
        
        # Aggregate SOAP metrics
        soap_metrics = []
        concept_metrics = []
        icd_metrics = []
        
        for result in results:
            if 'soap_scores' in result and result['soap_scores']:
                soap_metrics.append(result['soap_scores'])
            if 'concept_scores' in result and result['concept_scores']:
                concept_metrics.append(result['concept_scores'])
            if 'icd_scores' in result and result['icd_scores']:
                icd_metrics.append(result['icd_scores'])
        
        summary = {
            'total_evaluations': len(results),
            'timestamp': datetime.now().isoformat()
        }
        
        # SOAP metrics summary
        if soap_metrics:
            bleu_scores = [m.get('bleu_score', 0) for m in soap_metrics if 'bleu_score' in m]
            rouge_scores = [m.get('rouge_score', 0) for m in soap_metrics if 'rouge_score' in m]
            
            summary['soap_metrics'] = {
                'avg_bleu': np.mean(bleu_scores) if bleu_scores else 0.0,
                'avg_rouge_l': np.mean(rouge_scores) if rouge_scores else 0.0,
                'count': len(soap_metrics)
            }
        
        # Concept metrics summary
        if concept_metrics:
            f1_scores = [m.get('f1_score', 0) for m in concept_metrics if 'f1_score' in m]
            precision_scores = [m.get('precision', 0) for m in concept_metrics if 'precision' in m]
            
            summary['concept_metrics'] = {
                'avg_f1': np.mean(f1_scores) if f1_scores else 0.0,
                'avg_precision': np.mean(precision_scores) if precision_scores else 0.0,
                'count': len(concept_metrics)
            }
        
        # ICD metrics summary
        if icd_metrics:
            accuracy_scores = [m.get('accuracy', 0) for m in icd_metrics if 'accuracy' in m]
            f1_scores = [m.get('f1_score', 0) for m in icd_metrics if 'f1_score' in m]
            
            summary['icd_metrics'] = {
                'avg_accuracy': np.mean(accuracy_scores) if accuracy_scores else 0.0,
                'avg_f1': np.mean(f1_scores) if f1_scores else 0.0,
                'count': len(icd_metrics)
            }
        
        return summary
