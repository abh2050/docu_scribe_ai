from typing import Dict, Any, List, Tuple
import csv
import json
import os
from fuzzywuzzy import fuzz, process
from agents.base_agent import BaseAgent

class ICDMapperAgent(BaseAgent):
    """Agent responsible for mapping medical concepts to ICD-10 codes"""
    
    def __init__(self):
        super().__init__("ICDMapperAgent")
        self.icd10_data = self.load_icd10_data()
        self.condition_mappings = self.load_condition_mappings()
        self.confidence_threshold = 70  # Fuzzy matching threshold
    
    def process(self, input_data) -> List[Dict[str, Any]]:
        """Process input data - alias for map_to_icd10 method"""
        return self.map_to_icd10(input_data)
    
    def load_icd10_data(self) -> Dict[str, Dict[str, str]]:
        """Load ICD-10 codes and descriptions"""
        icd10_file = os.path.join("data", "icd10_codes.csv")
        
        # If file doesn't exist, create sample data
        if not os.path.exists(icd10_file):
            self.create_sample_icd10_data(icd10_file)
        
        icd10_dict = {}
        try:
            with open(icd10_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    code = row.get('code', '').strip()
                    description = row.get('description', '').strip()
                    category = row.get('category', '').strip()
                    
                    if code and description:
                        icd10_dict[code] = {
                            'description': description,
                            'category': category,
                            'keywords': self.extract_keywords(description)
                        }
        except Exception as e:
            self.logger.error(f"Failed to load ICD-10 data: {e}")
            icd10_dict = self.get_default_icd10_data()
        
        return icd10_dict
    
    def create_sample_icd10_data(self, file_path: str):
        """Create sample ICD-10 data file"""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        sample_data = [
            {"code": "I10", "description": "Essential (primary) hypertension", "category": "Cardiovascular"},
            {"code": "I15", "description": "Secondary hypertension", "category": "Cardiovascular"},
            {"code": "E11", "description": "Type 2 diabetes mellitus", "category": "Endocrine"},
            {"code": "E10", "description": "Type 1 diabetes mellitus", "category": "Endocrine"},
            {"code": "F32", "description": "Major depressive disorder", "category": "Mental Health"},
            {"code": "F41", "description": "Anxiety disorders", "category": "Mental Health"},
            {"code": "J45", "description": "Asthma", "category": "Respiratory"},
            {"code": "J44", "description": "Chronic obstructive pulmonary disease", "category": "Respiratory"},
            {"code": "M79.1", "description": "Myalgia", "category": "Musculoskeletal"},
            {"code": "M79.2", "description": "Neuralgia and neuritis", "category": "Musculoskeletal"},
            {"code": "R50", "description": "Fever", "category": "Symptoms"},
            {"code": "R51", "description": "Headache", "category": "Symptoms"},
            {"code": "R06.02", "description": "Shortness of breath", "category": "Symptoms"},
            {"code": "R25.1", "description": "Tremor", "category": "Symptoms"},
            {"code": "Z51.11", "description": "Encounter for antineoplastic chemotherapy", "category": "Factors"},
            {"code": "Z00.00", "description": "Encounter for general adult medical examination", "category": "Factors"}
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            fieldnames = ['code', 'description', 'category']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sample_data)
    
    def get_default_icd10_data(self) -> Dict[str, Dict[str, str]]:
        """Get default ICD-10 data when file loading fails"""
        return {
            "I10": {"description": "Essential (primary) hypertension", "category": "Cardiovascular", "keywords": ["hypertension", "high blood pressure"]},
            "E11": {"description": "Type 2 diabetes mellitus", "category": "Endocrine", "keywords": ["diabetes", "blood sugar"]},
            "F32": {"description": "Major depressive disorder", "category": "Mental Health", "keywords": ["depression", "mood"]},
            "R51": {"description": "Headache", "category": "Symptoms", "keywords": ["headache", "head pain"]}
        }
    
    def load_condition_mappings(self) -> Dict[str, List[str]]:
        """Load mappings between common terms and medical conditions"""
        return {
            "hypertension": ["high blood pressure", "elevated bp", "htn"],
            "diabetes": ["blood sugar", "glucose", "diabetic"],
            "depression": ["mood disorder", "depressed", "sad"],
            "anxiety": ["anxious", "worried", "panic"],
            "asthma": ["breathing problems", "wheezing", "respiratory"],
            "headache": ["head pain", "migraine", "cephalalgia"],
            "fever": ["temperature", "febrile", "hot"],
            "pain": ["ache", "hurt", "discomfort", "sore"]
        }
    
    def map_to_icd10(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map extracted medical concepts to ICD-10 codes
        
        Args:
            concepts: List of extracted medical concepts
            
        Returns:
            List of ICD-10 code suggestions with confidence scores
        """
        try:
            self.log_activity("Starting ICD-10 mapping")
            
            icd_suggestions = []
            
            # Filter concepts that could map to ICD-10 codes
            mappable_concepts = self.filter_mappable_concepts(concepts)
            
            for concept in mappable_concepts:
                suggestions = self.find_matching_codes(concept)
                icd_suggestions.extend(suggestions)
            
            # Remove duplicates and rank by confidence
            icd_suggestions = self.deduplicate_and_rank_codes(icd_suggestions)
            
            # Add additional context information
            icd_suggestions = self.enrich_code_suggestions(icd_suggestions, concepts)
            
            self.log_activity("ICD-10 mapping completed", {"suggestions_count": len(icd_suggestions)})
            
            return icd_suggestions
            
        except Exception as e:
            return self.handle_error(e, "ICD-10 mapping")
    
    def filter_mappable_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter concepts that are likely to have ICD-10 mappings"""
        mappable_categories = ["conditions", "symptoms", "procedures"]
        
        mappable_concepts = []
        for concept in concepts:
            category = concept.get("category", "")
            confidence = concept.get("confidence", 0)
            is_negated = concept.get("is_negated", False)
            
            # Include concepts that are medical conditions/symptoms and not negated
            if (category in mappable_categories or 
                any(keyword in concept.get("text", "").lower() for keyword in ["pain", "ache", "disorder", "disease", "syndrome"]) and
                confidence >= 0.6 and not is_negated):
                mappable_concepts.append(concept)
        
        return mappable_concepts
    
    def find_matching_codes(self, concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find ICD-10 codes that match a given concept"""
        concept_text = concept.get("text", "").lower()
        suggestions = []
        
        # Direct fuzzy matching against ICD-10 descriptions
        for code, data in self.icd10_data.items():
            description = data["description"].lower()
            keywords = data.get("keywords", [])
            
            # Calculate fuzzy match score
            fuzzy_score = fuzz.partial_ratio(concept_text, description)
            
            # Check keyword matches
            keyword_score = 0
            for keyword in keywords:
                if keyword.lower() in concept_text:
                    keyword_score += 20
            
            # Combine scores
            total_score = max(fuzzy_score, keyword_score)
            
            if total_score >= self.confidence_threshold:
                suggestions.append({
                    "icd10_code": code,
                    "description": data["description"],
                    "category": data["category"],
                    "confidence_score": min(100, total_score) / 100.0,
                    "match_type": "fuzzy_match",
                    "source_concept": concept_text,
                    "matching_method": f"fuzzy:{fuzzy_score}, keyword:{keyword_score}"
                })
        
        # Try mapping through condition mappings
        mapping_suggestions = self.find_mapped_conditions(concept_text)
        suggestions.extend(mapping_suggestions)
        
        return suggestions
    
    def find_mapped_conditions(self, concept_text: str) -> List[Dict[str, Any]]:
        """Find ICD-10 codes through condition mapping"""
        suggestions = []
        
        for condition, synonyms in self.condition_mappings.items():
            # Check if concept matches any synonym
            for synonym in synonyms:
                if synonym.lower() in concept_text or concept_text in synonym.lower():
                    # Find ICD-10 codes for this condition
                    for code, data in self.icd10_data.items():
                        if condition.lower() in data["description"].lower():
                            suggestions.append({
                                "icd10_code": code,
                                "description": data["description"],
                                "category": data["category"],
                                "confidence_score": 0.8,
                                "match_type": "synonym_mapping",
                                "source_concept": concept_text,
                                "matching_method": f"synonym:{synonym}"
                            })
                            break
        
        return suggestions
    
    def deduplicate_and_rank_codes(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate codes and rank by confidence"""
        # Group by ICD-10 code
        code_groups = {}
        for suggestion in suggestions:
            code = suggestion["icd10_code"]
            if code not in code_groups or suggestion["confidence_score"] > code_groups[code]["confidence_score"]:
                code_groups[code] = suggestion
        
        # Convert back to list and sort by confidence
        unique_suggestions = list(code_groups.values())
        unique_suggestions.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        return unique_suggestions
    
    def enrich_code_suggestions(self, suggestions: List[Dict[str, Any]], original_concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add additional context and validation to code suggestions"""
        enriched_suggestions = []
        
        for suggestion in suggestions:
            # Add clinical context
            suggestion["clinical_context"] = self.extract_clinical_context(suggestion, original_concepts)
            
            # Add validation notes
            suggestion["validation_notes"] = self.generate_validation_notes(suggestion)
            
            # Add usage recommendations
            suggestion["usage_recommendation"] = self.generate_usage_recommendation(suggestion)
            
            enriched_suggestions.append(suggestion)
        
        return enriched_suggestions
    
    def extract_clinical_context(self, suggestion: Dict[str, Any], concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract relevant clinical context for the ICD-10 suggestion"""
        context = {
            "supporting_concepts": [],
            "related_symptoms": [],
            "mentioned_by": "unknown"
        }
        
        # Find supporting concepts
        source_concept = suggestion.get("source_concept", "")
        for concept in concepts:
            if source_concept in concept.get("text", "").lower():
                context["mentioned_by"] = concept.get("attributed_to", "unknown")
                context["supporting_concepts"].append(concept.get("text", ""))
        
        # Find related symptoms
        symptom_categories = ["symptoms", "vital_measurement"]
        for concept in concepts:
            if concept.get("category") in symptom_categories:
                context["related_symptoms"].append(concept.get("text", ""))
        
        return context
    
    def generate_validation_notes(self, suggestion: Dict[str, Any]) -> List[str]:
        """Generate validation notes for the ICD-10 suggestion"""
        notes = []
        confidence = suggestion.get("confidence_score", 0)
        
        if confidence >= 0.9:
            notes.append("High confidence match - likely accurate")
        elif confidence >= 0.7:
            notes.append("Good match - review for accuracy")
        else:
            notes.append("Lower confidence - requires clinical validation")
        
        match_type = suggestion.get("match_type", "")
        if match_type == "fuzzy_match":
            notes.append("Matched based on text similarity")
        elif match_type == "synonym_mapping":
            notes.append("Matched through synonym mapping")
        
        return notes
    
    def generate_usage_recommendation(self, suggestion: Dict[str, Any]) -> str:
        """Generate usage recommendation for the ICD-10 code"""
        confidence = suggestion.get("confidence_score", 0)
        category = suggestion.get("category", "")
        
        if confidence >= 0.9:
            return "Recommended for use - high confidence match"
        elif confidence >= 0.8:
            return "Consider for use - good match with clinical review"
        elif confidence >= 0.7:
            return "Use with caution - requires clinical validation"
        else:
            return "Not recommended - low confidence match"
    
    def extract_keywords(self, description: str) -> List[str]:
        """Extract keywords from ICD-10 description"""
        # Remove common words and extract meaningful terms
        stop_words = {"the", "and", "or", "of", "in", "on", "at", "to", "for", "with", "by"}
        words = description.lower().split()
        keywords = [word.strip("(),.-") for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def validate_icd10_code(self, code: str) -> Dict[str, Any]:
        """Validate an ICD-10 code format and existence"""
        validation_result = {
            "is_valid": False,
            "exists_in_database": False,
            "format_correct": False,
            "warnings": []
        }
        
        # Check basic format (simplified)
        import re
        if re.match(r'^[A-Z]\d{2}(\.[\dA-Z]+)?$', code):
            validation_result["format_correct"] = True
        else:
            validation_result["warnings"].append("Invalid ICD-10 code format")
        
        # Check if code exists in our database
        if code in self.icd10_data:
            validation_result["exists_in_database"] = True
        else:
            validation_result["warnings"].append("Code not found in database")
        
        validation_result["is_valid"] = validation_result["format_correct"] and validation_result["exists_in_database"]
        
        return validation_result
    
    def get_fallback_result(self) -> List[Dict[str, Any]]:
        """Provide fallback result when ICD-10 mapping fails"""
        return [
            {
                "icd10_code": "Z99.9",
                "description": "Dependence on unspecified enabling machine or device",
                "category": "Factors",
                "confidence_score": 0.1,
                "match_type": "fallback",
                "source_concept": "mapping_failed",
                "validation_notes": ["ICD-10 mapping system encountered an error"],
                "usage_recommendation": "Manual review required"
            }
        ]
