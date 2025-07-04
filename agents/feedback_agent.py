from typing import Dict, Any, List
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from agents.base_agent import BaseAgent

# Load environment variables
load_dotenv()

class FeedbackAgent(BaseAgent):
    """Agent responsible for handling human feedback and corrections"""
    
    def __init__(self):
        super().__init__("FeedbackAgent")
        
        # Initialize LLM for intelligent feedback analysis
        self.llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.model_name = os.getenv("DEFAULT_MODEL", "gpt-4")
        self.use_llm = os.getenv("USE_LLM_FOR_FEEDBACK", "true").lower() == "true"
        self.initialize_llm()
        
        self.feedback_history = []
        self.correction_patterns = {}
    
    def initialize_llm(self):
        """Initialize the LLM for enhanced feedback analysis"""
        self.client = None
        if not self.use_llm:
            self.logger.info("LLM disabled for feedback analysis, using rule-based only")
            return
            
        try:
            if self.llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    self.logger.warning("OPENAI_API_KEY not found, using rule-based analysis")
                    return
                    
                import openai
                self.client = openai.OpenAI(api_key=api_key)
                self.logger.info("OpenAI client initialized for feedback analysis")
                
            elif self.llm_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    self.logger.warning("ANTHROPIC_API_KEY not found, using rule-based analysis")
                    return
                    
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                self.logger.info("Anthropic client initialized for feedback analysis")
                
        except Exception as e:
            self.logger.warning(f"Failed to initialize LLM for feedback analysis: {e}")
            self.client = None
    
    def process(self, input_data) -> Dict[str, Any]:
        """Process input data - alias for process_feedback method"""
        return self.process_feedback(input_data)
    
    def process_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process human feedback and corrections using hybrid LLM + rule-based approach
        
        Args:
            feedback_data: Dictionary containing feedback information
            
        Returns:
            Dict containing processed feedback and recommendations
        """
        try:
            self.log_activity("Processing user feedback")
            
            # Validate feedback structure
            validated_feedback = self.validate_feedback(feedback_data)
            
            # Use LLM if available and enabled, otherwise fall back to rule-based
            if self.use_llm and self.client:
                llm_analysis = self.analyze_feedback_with_llm(validated_feedback)
                rule_analysis = self.analyze_feedback_patterns(validated_feedback)
                
                # Merge LLM and rule-based analysis, prioritizing LLM insights
                feedback_analysis = self.merge_feedback_analysis(llm_analysis, rule_analysis)
                
                # Generate LLM-enhanced improvement suggestions
                improvements = self.generate_improvement_suggestions_with_llm(validated_feedback)
            else:
                # Use rule-based analysis only
                feedback_analysis = self.analyze_feedback_patterns(validated_feedback)
                improvements = self.generate_improvement_suggestions(validated_feedback)
            
            # Store feedback for learning
            self.store_feedback(validated_feedback)
            
            # Update system parameters based on feedback
            system_updates = self.update_system_parameters(validated_feedback)
            
            result = {
                "feedback_id": self.generate_feedback_id(),
                "processed_feedback": validated_feedback,
                "analysis": feedback_analysis,
                "improvements": improvements,
                "system_updates": system_updates,
                "timestamp": datetime.now().isoformat()
            }
            
            self.log_activity("Feedback processing completed", {"feedback_id": result["feedback_id"]})
            
            return result
            
        except Exception as e:
            return self.handle_error(e, "feedback processing")
    
    def validate_feedback(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure the feedback data"""
        validated = {
            "soap_corrections": {},
            "concept_corrections": [],
            "icd_corrections": [],
            "overall_rating": None,
            "comments": "",
            "correction_type": "unknown"
        }
        
        # Process SOAP note corrections
        if "soap_corrections" in feedback_data:
            soap_feedback = feedback_data["soap_corrections"]
            for section in ["subjective", "objective", "assessment", "plan"]:
                if section in soap_feedback:
                    validated["soap_corrections"][section] = {
                        "original": soap_feedback[section].get("original", ""),
                        "corrected": soap_feedback[section].get("corrected", ""),
                        "correction_type": self.classify_correction_type(
                            soap_feedback[section].get("original", ""),
                            soap_feedback[section].get("corrected", "")
                        )
                    }
        
        # Process concept corrections
        if "concept_corrections" in feedback_data:
            for concept_correction in feedback_data["concept_corrections"]:
                validated["concept_corrections"].append({
                    "original_concept": concept_correction.get("original", ""),
                    "corrected_concept": concept_correction.get("corrected", ""),
                    "action": concept_correction.get("action", "modify"),  # add, remove, modify
                    "reason": concept_correction.get("reason", "")
                })
        
        # Process ICD-10 corrections
        if "icd_corrections" in feedback_data:
            for icd_correction in feedback_data["icd_corrections"]:
                validated["icd_corrections"].append({
                    "original_code": icd_correction.get("original_code", ""),
                    "corrected_code": icd_correction.get("corrected_code", ""),
                    "action": icd_correction.get("action", "modify"),
                    "reason": icd_correction.get("reason", "")
                })
        
        # Process overall feedback
        validated["overall_rating"] = feedback_data.get("overall_rating")
        validated["comments"] = feedback_data.get("comments", "")
        
        return validated
    
    def classify_correction_type(self, original: str, corrected: str) -> str:
        """Classify the type of correction made"""
        if not original and corrected:
            return "addition"
        elif original and not corrected:
            return "deletion"
        elif original != corrected:
            if len(corrected) > len(original) * 1.5:
                return "major_expansion"
            elif len(corrected) < len(original) * 0.5:
                return "major_reduction"
            else:
                return "modification"
        else:
            return "no_change"
    
    def analyze_feedback_patterns(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in the feedback to identify systematic issues"""
        analysis = {
            "common_issues": [],
            "improvement_areas": [],
            "accuracy_metrics": {},
            "user_satisfaction": {}
        }
        
        # Analyze SOAP corrections
        soap_issues = self.analyze_soap_corrections(feedback.get("soap_corrections", {}))
        analysis["common_issues"].extend(soap_issues)
        
        # Analyze concept extraction accuracy
        concept_accuracy = self.analyze_concept_accuracy(feedback.get("concept_corrections", []))
        analysis["accuracy_metrics"]["concept_extraction"] = concept_accuracy
        
        # Analyze ICD mapping accuracy
        icd_accuracy = self.analyze_icd_accuracy(feedback.get("icd_corrections", []))
        analysis["accuracy_metrics"]["icd_mapping"] = icd_accuracy
        
        # Analyze user satisfaction
        overall_rating = feedback.get("overall_rating")
        if overall_rating is not None:
            analysis["user_satisfaction"] = {
                "rating": overall_rating,
                "category": self.categorize_satisfaction(overall_rating)
            }
        
        return analysis
    
    def analyze_soap_corrections(self, soap_corrections: Dict[str, Any]) -> List[str]:
        """Analyze SOAP note corrections to identify common issues"""
        issues = []
        
        for section, correction in soap_corrections.items():
            correction_type = correction.get("correction_type", "")
            
            if correction_type == "addition":
                issues.append(f"SOAP {section} section missing information")
            elif correction_type == "major_expansion":
                issues.append(f"SOAP {section} section too brief")
            elif correction_type == "major_reduction":
                issues.append(f"SOAP {section} section too verbose")
            elif correction_type == "modification":
                issues.append(f"SOAP {section} section accuracy issues")
        
        return issues
    
    def analyze_concept_accuracy(self, concept_corrections: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze concept extraction accuracy based on corrections"""
        if not concept_corrections:
            return {"accuracy": 1.0, "precision": 1.0, "recall": 1.0}
        
        additions = sum(1 for c in concept_corrections if c.get("action") == "add")
        removals = sum(1 for c in concept_corrections if c.get("action") == "remove")
        modifications = sum(1 for c in concept_corrections if c.get("action") == "modify")
        
        total_corrections = len(concept_corrections)
        
        # Simplified accuracy calculation
        accuracy = max(0.0, 1.0 - (total_corrections / max(10, total_corrections + 10)))
        precision = max(0.0, 1.0 - (removals / max(1, total_corrections)))
        recall = max(0.0, 1.0 - (additions / max(1, total_corrections)))
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "total_corrections": total_corrections
        }
    
    def analyze_icd_accuracy(self, icd_corrections: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze ICD mapping accuracy based on corrections"""
        if not icd_corrections:
            return {"accuracy": 1.0, "correct_mappings": 1.0}
        
        total_corrections = len(icd_corrections)
        
        # Calculate accuracy based on corrections needed
        accuracy = max(0.0, 1.0 - (total_corrections / max(5, total_corrections + 5)))
        
        return {
            "accuracy": accuracy,
            "total_corrections": total_corrections,
            "needs_improvement": total_corrections > 2
        }
    
    def categorize_satisfaction(self, rating: float) -> str:
        """Categorize user satisfaction rating"""
        if rating >= 4.5:
            return "excellent"
        elif rating >= 3.5:
            return "good"
        elif rating >= 2.5:
            return "acceptable"
        elif rating >= 1.5:
            return "poor"
        else:
            return "very_poor"
    
    def generate_improvement_suggestions(self, feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate suggestions for system improvement based on feedback"""
        suggestions = []
        
        # Analyze SOAP corrections for suggestions
        soap_corrections = feedback.get("soap_corrections", {})
        for section, correction in soap_corrections.items():
            correction_type = correction.get("correction_type", "")
            
            if correction_type == "addition":
                suggestions.append({
                    "area": "soap_generation",
                    "section": section,
                    "suggestion": f"Improve {section} section completeness",
                    "priority": "high",
                    "implementation": "Enhance prompts to capture more detail"
                })
            elif correction_type == "major_expansion":
                suggestions.append({
                    "area": "soap_generation",
                    "section": section,
                    "suggestion": f"Increase detail level in {section} section",
                    "priority": "medium",
                    "implementation": "Adjust generation parameters for more verbose output"
                })
        
        # Analyze concept corrections for suggestions
        concept_corrections = feedback.get("concept_corrections", [])
        if len(concept_corrections) > 2:
            suggestions.append({
                "area": "concept_extraction",
                "suggestion": "Improve medical concept recognition accuracy",
                "priority": "high",
                "implementation": "Retrain concept extraction models or update medical vocabularies"
            })
        
        # Analyze ICD corrections for suggestions
        icd_corrections = feedback.get("icd_corrections", [])
        if len(icd_corrections) > 1:
            suggestions.append({
                "area": "icd_mapping",
                "suggestion": "Improve ICD-10 code mapping accuracy",
                "priority": "medium",
                "implementation": "Update ICD mapping algorithms or expand code database"
            })
        
        return suggestions
    
    def analyze_feedback_with_llm(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze feedback using LLM for intelligent insights
        """
        if not self.client:
            self.logger.warning("LLM client not available, falling back to rule-based analysis")
            return self.analyze_feedback_patterns(feedback)
        
        try:
            feedback_summary = self.prepare_feedback_summary(feedback)
            
            prompt = f"""
You are a healthcare AI system analyst. Analyze this feedback and provide insights:

Feedback: {feedback_summary}

Return JSON with:
{{
    "root_causes": ["list of issues"],
    "priority_areas": ["improvement areas"],
    "satisfaction_assessment": {{
        "level": "excellent/good/fair/poor",
        "key_concerns": ["concerns"],
        "positive_aspects": ["positives"]
    }},
    "reliability_score": 0.8
}}
"""

            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a healthcare AI analyst. Return valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=600
                )
                content = response.choices[0].message.content.strip()
                
            elif self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=600,
                    temperature=0.1,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()
            
            # Parse JSON response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            analysis = json.loads(content)
            analysis["source"] = "llm"
            
            self.logger.info("LLM feedback analysis completed")
            return analysis
            
        except Exception as e:
            self.logger.error(f"LLM feedback analysis failed: {e}")
            return self.analyze_feedback_patterns(feedback)
    
    def prepare_feedback_summary(self, feedback: Dict[str, Any]) -> str:
        """Prepare feedback summary for LLM analysis"""
        summary_parts = []
        
        soap_corrections = feedback.get("soap_corrections", {})
        if soap_corrections:
            soap_issues = [f"{section}: {correction.get('correction_type', 'modification')}" 
                          for section, correction in soap_corrections.items()]
            summary_parts.append(f"SOAP corrections: {', '.join(soap_issues)}")
        
        concept_corrections = feedback.get("concept_corrections", [])
        if concept_corrections:
            summary_parts.append(f"Concept corrections: {len(concept_corrections)}")
        
        icd_corrections = feedback.get("icd_corrections", [])
        if icd_corrections:
            summary_parts.append(f"ICD corrections: {len(icd_corrections)}")
        
        overall_rating = feedback.get("overall_rating")
        if overall_rating is not None:
            summary_parts.append(f"Rating: {overall_rating}/5")
        
        comments = feedback.get("comments", "")
        if comments:
            summary_parts.append(f"Comments: {comments}")
        
        return " | ".join(summary_parts) if summary_parts else "No feedback provided"
    
    def generate_improvement_suggestions_with_llm(self, feedback: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate LLM-enhanced improvement suggestions"""
        if not self.client:
            return self.generate_improvement_suggestions(feedback)
        
        try:
            feedback_summary = self.prepare_feedback_summary(feedback)
            
            prompt = f"""
Based on this healthcare AI feedback, suggest improvements:

Feedback: {feedback_summary}

Return JSON array:
[
    {{
        "area": "system component",
        "suggestion": "specific improvement",
        "priority": "high/medium/low",
        "implementation": "how to implement"
    }}
]
"""

            if self.llm_provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "Return valid JSON array of improvements."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=500
                )
                content = response.choices[0].message.content.strip()
                
            elif self.llm_provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=500,
                    temperature=0.2,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()
            
            # Parse JSON response
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            suggestions = json.loads(content)
            
            # Add source and combine with rule-based
            for suggestion in suggestions:
                suggestion["source"] = "llm"
            
            rule_suggestions = self.generate_improvement_suggestions(feedback)
            return suggestions + rule_suggestions
            
        except Exception as e:
            self.logger.error(f"LLM suggestions failed: {e}")
            return self.generate_improvement_suggestions(feedback)
    
    def merge_feedback_analysis(self, llm_analysis: Dict[str, Any], rule_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Merge LLM and rule-based analysis results"""
        merged = {
            "common_issues": [],
            "improvement_areas": [],
            "accuracy_metrics": rule_analysis.get("accuracy_metrics", {}),
            "user_satisfaction": {},
            "analysis_source": "hybrid"
        }
        
        # Use LLM insights if available
        if llm_analysis.get("source") == "llm":
            merged["common_issues"] = llm_analysis.get("root_causes", [])
            merged["improvement_areas"] = llm_analysis.get("priority_areas", [])
            
            satisfaction = llm_analysis.get("satisfaction_assessment", {})
            merged["user_satisfaction"] = {
                "level": satisfaction.get("level", "fair"),
                "key_concerns": satisfaction.get("key_concerns", []),
                "positive_aspects": satisfaction.get("positive_aspects", [])
            }
        else:
            # Fall back to rule-based
            merged["common_issues"] = rule_analysis.get("common_issues", [])
            merged["improvement_areas"] = rule_analysis.get("improvement_areas", [])
            merged["user_satisfaction"] = rule_analysis.get("user_satisfaction", {})
        
        self.logger.info(f"Merged analysis from {'LLM + rule-based' if llm_analysis.get('source') == 'llm' else 'rule-based only'}")
        return merged
    
    def store_feedback(self, feedback: Dict[str, Any]):
        """Store feedback for future learning and analysis"""
        feedback_entry = {
            "timestamp": datetime.now().isoformat(),
            "feedback": feedback,
            "session_id": self.generate_session_id()
        }
        
        self.feedback_history.append(feedback_entry)
        
        # Keep only recent feedback (last 100 entries)
        if len(self.feedback_history) > 100:
            self.feedback_history = self.feedback_history[-100:]
    
    def update_system_parameters(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """Update system parameters based on feedback"""
        updates = {
            "confidence_thresholds": {},
            "model_parameters": {},
            "processing_flags": {}
        }
        
        # Adjust confidence thresholds based on accuracy
        concept_corrections = feedback.get("concept_corrections", [])
        if len(concept_corrections) > 3:
            updates["confidence_thresholds"]["concept_extraction"] = "increase"
        
        icd_corrections = feedback.get("icd_corrections", [])
        if len(icd_corrections) > 2:
            updates["confidence_thresholds"]["icd_mapping"] = "increase"
        
        # Adjust SOAP generation parameters
        soap_corrections = feedback.get("soap_corrections", {})
        for section, correction in soap_corrections.items():
            if correction.get("correction_type") == "major_expansion":
                updates["model_parameters"][f"soap_{section}_verbosity"] = "increase"
            elif correction.get("correction_type") == "major_reduction":
                updates["model_parameters"][f"soap_{section}_verbosity"] = "decrease"
        
        return updates
    
    def generate_feedback_report(self) -> Dict[str, Any]:
        """Generate a comprehensive feedback report"""
        if not self.feedback_history:
            return {"message": "No feedback data available"}
        
        recent_feedback = self.feedback_history[-10:]  # Last 10 feedback entries
        
        # Calculate overall metrics
        ratings = [f["feedback"].get("overall_rating") for f in recent_feedback if f["feedback"].get("overall_rating")]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        
        # Count correction types
        total_soap_corrections = sum(len(f["feedback"].get("soap_corrections", {})) for f in recent_feedback)
        total_concept_corrections = sum(len(f["feedback"].get("concept_corrections", [])) for f in recent_feedback)
        total_icd_corrections = sum(len(f["feedback"].get("icd_corrections", [])) for f in recent_feedback)
        
        report = {
            "summary": {
                "total_feedback_entries": len(recent_feedback),
                "average_rating": avg_rating,
                "total_corrections": total_soap_corrections + total_concept_corrections + total_icd_corrections
            },
            "correction_breakdown": {
                "soap_corrections": total_soap_corrections,
                "concept_corrections": total_concept_corrections,
                "icd_corrections": total_icd_corrections
            },
            "trends": self.identify_feedback_trends(recent_feedback),
            "recommendations": self.generate_system_recommendations(recent_feedback)
        }
        
        return report
    
    def identify_feedback_trends(self, feedback_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify trends in feedback over time"""
        if len(feedback_history) < 3:
            return {"message": "Insufficient data for trend analysis"}
        
        # Analyze rating trends
        ratings = [f["feedback"].get("overall_rating", 0) for f in feedback_history if f["feedback"].get("overall_rating")]
        
        trends = {
            "rating_trend": "stable",
            "improvement_areas": [],
            "deteriorating_areas": []
        }
        
        if len(ratings) >= 3:
            recent_avg = sum(ratings[-3:]) / 3
            older_avg = sum(ratings[:-3]) / len(ratings[:-3]) if len(ratings) > 3 else recent_avg
            
            if recent_avg > older_avg + 0.3:
                trends["rating_trend"] = "improving"
            elif recent_avg < older_avg - 0.3:
                trends["rating_trend"] = "declining"
        
        return trends
    
    def generate_system_recommendations(self, feedback_history: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for system improvement"""
        recommendations = []
        
        # Analyze common issues
        common_issues = {}
        for entry in feedback_history:
            feedback = entry["feedback"]
            
            # Count SOAP issues by section
            for section in feedback.get("soap_corrections", {}):
                common_issues[f"soap_{section}"] = common_issues.get(f"soap_{section}", 0) + 1
            
            # Count concept issues
            if feedback.get("concept_corrections"):
                common_issues["concept_extraction"] = common_issues.get("concept_extraction", 0) + 1
            
            # Count ICD issues
            if feedback.get("icd_corrections"):
                common_issues["icd_mapping"] = common_issues.get("icd_mapping", 0) + 1
        
        # Generate recommendations based on frequent issues
        for issue, count in common_issues.items():
            if count >= len(feedback_history) * 0.3:  # Issue appears in 30% of feedback
                if issue.startswith("soap_"):
                    section = issue.replace("soap_", "")
                    recommendations.append(f"Focus on improving SOAP {section} section generation")
                elif issue == "concept_extraction":
                    recommendations.append("Enhance medical concept extraction accuracy")
                elif issue == "icd_mapping":
                    recommendations.append("Improve ICD-10 code mapping precision")
        
        return recommendations
    
    def generate_feedback_id(self) -> str:
        """Generate a unique feedback ID"""
        return f"fb_{int(datetime.now().timestamp())}"
    
    def generate_session_id(self) -> str:
        """Generate a session ID"""
        return f"session_{int(datetime.now().timestamp())}"
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback result when feedback processing fails"""
        return {
            "feedback_id": "error",
            "processed_feedback": {},
            "analysis": {"error": "Feedback processing failed"},
            "improvements": [],
            "system_updates": {},
            "timestamp": datetime.now().isoformat()
        }
