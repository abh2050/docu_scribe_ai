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
        
        # Load mappings from external file
        self.specific_condition_mappings = {}
        self.synonym_mappings = {}
        self.medication_exclusions = []
        self.load_external_mappings()
        
        self.confidence_threshold = 70  # Fuzzy matching threshold
    
    def process(self, input_data) -> List[Dict[str, Any]]:
        """Process input data - alias for map_to_icd10 method"""
        return self.map_to_icd10(input_data)
    
    def load_icd10_data(self) -> Dict[str, Dict[str, str]]:
        """Load ICD-10 codes and descriptions from official April 2025 data"""
        # Primary file: April 2025 ICD-10-CM codes
        primary_file = os.path.join("data", "Code-desciptions-April-2025", "icd10cm-codes-April-2025.txt")
        
        # Fallback to CSV file if primary not available
        csv_file = os.path.join("data", "icd10_codes.csv")
        
        icd10_dict = {}
        
        try:
            # Try to load from primary codes file first
            if os.path.exists(primary_file):
                self.logger.info(f"Loading ICD-10 data from {primary_file}")
                icd10_dict = self._load_from_codes_file(primary_file)
            elif os.path.exists(csv_file):
                self.logger.info(f"Loading ICD-10 data from {csv_file}")
                icd10_dict = self._load_from_csv_file(csv_file)
            else:
                self.logger.warning("No ICD-10 files found, using default data")
                icd10_dict = self.get_default_icd10_data()
                
        except Exception as e:
            self.logger.error(f"Failed to load ICD-10 data: {e}")
            icd10_dict = self.get_default_icd10_data()
        
        self.logger.info(f"Loaded {len(icd10_dict)} ICD-10 codes")
        return icd10_dict
    
    def _load_from_codes_file(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """Load ICD-10 data from codes file format: 'CODE    DESCRIPTION'"""
        icd10_dict = {}
        
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                    
                # Split on whitespace, expecting: CODE    DESCRIPTION
                parts = line.split(None, 1)  # Split on any whitespace, max 1 split
                if len(parts) >= 2:
                    code = parts[0].strip()
                    description = parts[1].strip()
                    
                    if code and description:
                        # Determine category based on code prefix
                        category = self._determine_category_from_code(code)
                        
                        icd10_dict[code] = {
                            'description': description,
                            'category': category,
                            'keywords': self.extract_keywords(description)
                        }
                elif len(parts) == 1:
                    self.logger.debug(f"Line {line_num}: No description found for code {parts[0]}")
                    
        return icd10_dict

    def _load_from_csv_file(self, file_path: str) -> Dict[str, Dict[str, str]]:
        """Load ICD-10 data from CSV file"""
        icd10_dict = {}
        
        # If file doesn't exist, create sample data
        if not os.path.exists(file_path):
            self.create_sample_icd10_data(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
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
            self.logger.error(f"Failed to load CSV ICD-10 data: {e}")
        
        return icd10_dict

    def _determine_category_from_code(self, code: str) -> str:
        """Determine ICD-10 category based on code prefix"""
        if not code:
            return "Unknown"
            
        prefix = code[0].upper()
        
        # ICD-10-CM category mapping based on first letter
        category_mapping = {
            'A': 'Infectious and Parasitic Diseases',
            'B': 'Infectious and Parasitic Diseases', 
            'C': 'Neoplasms',
            'D': 'Diseases of Blood and Immune System',
            'E': 'Endocrine, Nutritional and Metabolic Diseases',
            'F': 'Mental, Behavioral and Neurodevelopmental Disorders',
            'G': 'Diseases of the Nervous System',
            'H': 'Diseases of Eye/Ear and Adnexa',
            'I': 'Diseases of the Circulatory System',
            'J': 'Diseases of the Respiratory System',
            'K': 'Diseases of the Digestive System',
            'L': 'Diseases of the Skin and Subcutaneous Tissue',
            'M': 'Diseases of the Musculoskeletal System',
            'N': 'Diseases of the Genitourinary System',
            'O': 'Pregnancy, Childbirth and the Puerperium',
            'P': 'Perinatal Period Conditions',
            'Q': 'Congenital Malformations and Chromosomal Abnormalities',
            'R': 'Symptoms, Signs and Abnormal Clinical Findings',
            'S': 'Injury, Poisoning and External Causes',
            'T': 'Injury, Poisoning and External Causes',
            'V': 'External Causes of Morbidity',
            'W': 'External Causes of Morbidity',
            'X': 'External Causes of Morbidity',
            'Y': 'External Causes of Morbidity',
            'Z': 'Factors Influencing Health Status'
        }
        
        return category_mapping.get(prefix, 'Unknown')

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
    
    def load_external_mappings(self):
        """Load mappings from external JSON file"""
        mappings_file = os.path.join("data", "icd_condition_mappings.json")
        
        try:
            if os.path.exists(mappings_file):
                with open(mappings_file, 'r', encoding='utf-8') as file:
                    mappings_data = json.load(file)
                    
                    self.specific_condition_mappings = mappings_data.get("specific_condition_mappings", {})
                    self.synonym_mappings = mappings_data.get("synonym_mappings", {})
                    self.medication_exclusions = mappings_data.get("medication_exclusions", [])
                    
                    self.logger.info(f"Loaded {len(self.specific_condition_mappings)} specific conditions, "
                                   f"{len(self.synonym_mappings)} synonym groups, "
                                   f"{len(self.medication_exclusions)} medication exclusions")
            else:
                self.logger.warning(f"External mappings file not found: {mappings_file}")
                # Use fallback mappings
                self.specific_condition_mappings = self.get_fallback_specific_mappings()
                self.synonym_mappings = self.get_fallback_synonym_mappings()
                self.medication_exclusions = self.get_fallback_medication_exclusions()
                
        except Exception as e:
            self.logger.error(f"Failed to load external mappings: {e}")
            # Use fallback mappings
            self.specific_condition_mappings = self.get_fallback_specific_mappings()
            self.synonym_mappings = self.get_fallback_synonym_mappings()
            self.medication_exclusions = self.get_fallback_medication_exclusions()

    def get_fallback_specific_mappings(self) -> Dict[str, List[str]]:
        """Get fallback specific condition mappings when external file fails"""
        return {
            "headache": ["R519", "R510", "G439"],
            "hypertension": ["I10", "I11"],
            "diabetes": ["E119", "E11"],
            "depression": ["F329", "F32"],
            "anxiety": ["F419", "F41"]
        }

    def get_fallback_synonym_mappings(self) -> Dict[str, List[str]]:
        """Get fallback synonym mappings when external file fails"""
        return {
            "hypertension": ["high blood pressure", "elevated bp", "htn"],
            "diabetes": ["blood sugar", "glucose", "diabetic"],
            "depression": ["mood disorder", "depressed", "sad"],
            "anxiety": ["anxious", "worried", "panic"],
            "headache": ["head pain", "migraine", "cephalalgia"]
        }

    def get_fallback_medication_exclusions(self) -> List[str]:
        """Get fallback medication exclusions when external file fails"""
        return ["ibuprofen", "tylenol", "acetaminophen", "aspirin", "medication"]
    
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
            
            # Defensive programming: ensure concepts is a list
            if not isinstance(concepts, list):
                self.logger.warning(f"Expected list of concepts, got {type(concepts)}")
                return []
            
            # Defensive programming: ensure each concept is a dictionary
            valid_concepts = []
            for i, concept in enumerate(concepts):
                if isinstance(concept, dict):
                    valid_concepts.append(concept)
                elif isinstance(concept, str):
                    # Convert string to dict format
                    valid_concepts.append({
                        "text": concept,
                        "category": "unknown",
                        "confidence": 0.7
                    })
                else:
                    self.logger.warning(f"Concept {i} has unexpected type {type(concept)}: {concept}")
            
            if not valid_concepts:
                self.logger.warning("No valid concepts found for ICD mapping")
                return []
            
            icd_suggestions = []
            
            # Filter concepts that could map to ICD-10 codes
            mappable_concepts = self.filter_mappable_concepts(valid_concepts)
            
            for concept in mappable_concepts:
                suggestions = self.find_matching_codes(concept)
                icd_suggestions.extend(suggestions)
            
            # Remove duplicates and rank by confidence
            icd_suggestions = self.deduplicate_and_rank_codes(icd_suggestions)
            
            # Add additional context information
            icd_suggestions = self.enrich_code_suggestions(icd_suggestions, valid_concepts)
            
            self.log_activity("ICD-10 mapping completed", {"suggestions_count": len(icd_suggestions)})
            
            return icd_suggestions
            
        except Exception as e:
            self.logger.error(f"Error in ICD mapping: {e}")
            return self.handle_error(e, "ICD-10 mapping")
    
    def filter_mappable_concepts(self, concepts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter concepts that are likely to have ICD-10 mappings"""
        mappable_categories = ["condition", "conditions", "symptom", "symptoms", "procedure", "procedures"]
        
        mappable_concepts = []
        for concept in concepts:
            try:
                # Defensive programming: ensure concept is a dict
                if not isinstance(concept, dict):
                    self.logger.warning(f"Skipping non-dict concept: {concept}")
                    continue
                    
                category = concept.get("category", "")
                confidence = concept.get("confidence", 0)
                is_negated = concept.get("is_negated", False)
                concept_text = concept.get("text", concept.get("concept", "")).lower()
                
                # Skip if no concept text
                if not concept_text:
                    continue
                
                # Skip medication exclusions
                if any(med.lower() in concept_text for med in self.medication_exclusions):
                    continue
                
                # Include concepts that are medical conditions/symptoms and not negated
                if (category in mappable_categories or 
                    any(keyword in concept_text for keyword in ["pain", "ache", "disorder", "disease", "syndrome"]) and
                    confidence >= 0.6 and not is_negated):
                    mappable_concepts.append(concept)
                    
            except Exception as e:
                self.logger.warning(f"Error processing concept {concept}: {e}")
                continue
        
        return mappable_concepts
    
    def find_matching_codes(self, concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find ICD-10 codes that match a given concept"""
        concept_text = concept.get("text", "").lower()
        suggestions = []
        
        # Try mapping through specific condition mappings FIRST (highest priority)
        specific_suggestions = self.find_specific_condition_matches(concept_text)
        suggestions.extend(specific_suggestions)
        
        # Try mapping through synonym mappings SECOND (high priority)
        synonym_suggestions = self.find_synonym_matches(concept_text)
        suggestions.extend(synonym_suggestions)
        
        # Only do fuzzy matching if no specific matches found
        if not suggestions:
            # Direct fuzzy matching against ICD-10 descriptions (lowest priority)
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
        
        return suggestions
    
    def find_specific_condition_matches(self, concept_text: str) -> List[Dict[str, Any]]:
        """Find ICD-10 codes through specific condition mappings"""
        suggestions = []
        
        for condition, icd_codes in self.specific_condition_mappings.items():
            # Check for exact match or partial match
            match_found = False
            
            # Exact match
            if condition.lower() == concept_text:
                match_found = True
            # Condition contains concept or concept contains condition  
            elif condition.lower() in concept_text or concept_text in condition.lower():
                match_found = True
            # Word-level matching for multi-word concepts
            elif any(word in condition.lower() for word in concept_text.split() if len(word) > 3):
                match_found = True
            # Special handling for common patterns
            elif concept_text in ["elevated", "high"] and "blood pressure" in condition.lower():
                match_found = True
            elif concept_text == "blood pressure" and "hypertension" in condition.lower():
                match_found = True
                
            if match_found:
                for code in icd_codes:
                    if code in self.icd10_data:
                        suggestions.append({
                            "icd10_code": code,
                            "description": self.icd10_data[code]["description"],
                            "category": self.icd10_data[code]["category"],
                            "confidence_score": 0.95,  # High confidence for specific mappings
                            "match_type": "specific_mapping",
                            "source_concept": concept_text,
                            "matching_method": f"specific_condition_mapping:{condition}→{code}"
                        })
        
        return suggestions

    def find_synonym_matches(self, concept_text: str) -> List[Dict[str, Any]]:
        """Find ICD-10 codes through synonym mappings"""
        suggestions = []
        
        for condition, synonyms in self.synonym_mappings.items():
            # Check if concept matches any synonym
            for synonym in synonyms:
                if (synonym.lower() in concept_text or 
                    concept_text in synonym.lower() or
                    any(word in synonym.lower() for word in concept_text.split() if len(word) > 3)):
                    
                    # Look for specific condition mappings first
                    if condition in self.specific_condition_mappings:
                        for code in self.specific_condition_mappings[condition]:
                            if code in self.icd10_data:
                                suggestions.append({
                                    "icd10_code": code,
                                    "description": self.icd10_data[code]["description"],
                                    "category": self.icd10_data[code]["category"],
                                    "confidence_score": 0.90,  # High confidence for synonym mappings
                                    "match_type": "synonym_mapping",
                                    "source_concept": concept_text,
                                    "matching_method": f"synonym:{synonym}→{condition}→{code}"
                                })
                    
                    # Also try fuzzy matching against the condition in ICD-10 data
                    for code, data in self.icd10_data.items():
                        description_lower = data["description"].lower()
                        if condition.lower() in description_lower:
                            suggestions.append({
                                "icd10_code": code,
                                "description": data["description"],
                                "category": data["category"],
                                "confidence_score": 0.85,
                                "match_type": "synonym_mapping",
                                "source_concept": concept_text,
                                "matching_method": f"synonym:{synonym}→{condition}→fuzzy_match"
                            })
                            # Limit to prevent too many matches
                            break
        
        return suggestions
    
    def deduplicate_and_rank_codes(self, suggestions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate codes and rank by confidence"""
        # Group by ICD-10 code, keeping the highest confidence version
        code_groups = {}
        for suggestion in suggestions:
            code = suggestion["icd10_code"]
            if code not in code_groups or suggestion["confidence_score"] > code_groups[code]["confidence_score"]:
                code_groups[code] = suggestion
        
        # Convert back to list and sort by confidence
        unique_suggestions = list(code_groups.values())
        unique_suggestions.sort(key=lambda x: x["confidence_score"], reverse=True)
        
        # Separate by match type and prioritize appropriately
        specific_mappings = [s for s in unique_suggestions if s.get("match_type") == "specific_mapping"]
        synonym_mappings = [s for s in unique_suggestions if s.get("match_type") == "synonym_mapping"]
        fuzzy_mappings = [s for s in unique_suggestions if s.get("match_type") == "fuzzy_match"]
        
        # Take all high-confidence specific mappings first, then fill with others
        final_suggestions = []
        final_suggestions.extend(specific_mappings[:5])  # Take up to 5 specific mappings
        
        # If we have space, add some synonym mappings
        remaining_slots = max(0, 6 - len(final_suggestions))
        final_suggestions.extend(synonym_mappings[:remaining_slots])
        
        # If we still have space, add fuzzy mappings
        remaining_slots = max(0, 6 - len(final_suggestions))
        final_suggestions.extend(fuzzy_mappings[:remaining_slots])
        
        # Remove any duplicates that might have slipped through
        seen_codes = set()
        deduplicated = []
        for suggestion in final_suggestions:
            code = suggestion["icd10_code"]
            if code not in seen_codes:
                seen_codes.add(code)
                deduplicated.append(suggestion)
        
        return deduplicated
    
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
