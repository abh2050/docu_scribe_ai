from typing import Dict, Any, List
import json
from datetime import datetime
from agents.base_agent import BaseAgent

class FormatterAgent(BaseAgent):
    """Agent responsible for formatting final output and preparing for EHR integration"""
    
    def __init__(self):
        super().__init__("FormatterAgent")
        self.supported_formats = ["fhir", "hl7", "json", "xml", "text"]
        self.default_format = "fhir"
    
    def process(self, input_data) -> Dict[str, Any]:
        """Process input data - expects tuple of (soap_notes, concepts, icd_codes, metadata, format)"""
        if isinstance(input_data, tuple) and len(input_data) >= 4:
            soap_notes, concepts, icd_codes, metadata = input_data[:4]
            output_format = input_data[4] if len(input_data) > 4 else "fhir"
            return self.format_output(soap_notes, concepts, icd_codes, metadata, output_format)
        else:
            # Fallback
            return self.format_output({}, [], [], {}, "fhir")
    
    def format_output(self, 
                     soap_notes: Dict[str, str],
                     concepts: List[Dict[str, Any]],
                     icd_codes: List[Dict[str, Any]],
                     metadata: Dict[str, Any],
                     output_format: str = "fhir") -> Dict[str, Any]:
        """
        Format the processed clinical data into the specified output format
        
        Args:
            soap_notes: Generated SOAP notes
            concepts: Extracted medical concepts
            icd_codes: Mapped ICD-10 codes
            metadata: Processing metadata
            output_format: Desired output format
            
        Returns:
            Dict containing formatted output
        """
        try:
            self.log_activity("Starting output formatting", {"format": output_format})
            
            # Validate input data
            validated_data = self.validate_input_data(soap_notes, concepts, icd_codes, metadata)
            
            # Format based on requested format
            if output_format.lower() == "fhir":
                formatted_output = self.format_to_fhir(validated_data)
            elif output_format.lower() == "hl7":
                formatted_output = self.format_to_hl7(validated_data)
            elif output_format.lower() == "json":
                formatted_output = self.format_to_json(validated_data)
            elif output_format.lower() == "xml":
                formatted_output = self.format_to_xml(validated_data)
            elif output_format.lower() == "text":
                formatted_output = self.format_to_text(validated_data)
            else:
                # Default to FHIR if format not supported
                formatted_output = self.format_to_fhir(validated_data)
            
            # Add metadata and validation
            final_output = self.add_output_metadata(formatted_output, output_format, metadata)
            
            self.log_activity("Output formatting completed", {"format": output_format})
            
            return final_output
            
        except Exception as e:
            return self.handle_error(e, "output formatting")
    
    def validate_input_data(self, soap_notes: Dict[str, str], concepts: List[Dict[str, Any]], 
                          icd_codes: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and structure input data"""
        validated = {
            "soap_notes": soap_notes or {},
            "concepts": concepts or [],
            "icd_codes": icd_codes or [],
            "metadata": metadata or {},
            "validation_results": {}
        }
        
        # Validate SOAP notes
        soap_validation = self.validate_soap_notes(soap_notes)
        validated["validation_results"]["soap_notes"] = soap_validation
        
        # Validate concepts
        concepts_validation = self.validate_concepts(concepts)
        validated["validation_results"]["concepts"] = concepts_validation
        
        # Validate ICD codes
        icd_validation = self.validate_icd_codes(icd_codes)
        validated["validation_results"]["icd_codes"] = icd_validation
        
        return validated
    
    def validate_soap_notes(self, soap_notes: Dict[str, str]) -> Dict[str, Any]:
        """Validate SOAP notes structure and content"""
        validation = {
            "is_valid": True,
            "missing_sections": [],
            "warnings": [],
            "completeness_score": 0.0
        }
        
        required_sections = ["subjective", "objective", "assessment", "plan"]
        present_sections = 0
        
        for section in required_sections:
            if section not in soap_notes or not soap_notes[section].strip():
                validation["missing_sections"].append(section)
                validation["is_valid"] = False
            else:
                present_sections += 1
                # Check for minimum content
                if len(soap_notes[section].strip()) < 10:
                    validation["warnings"].append(f"{section} section is very brief")
        
        validation["completeness_score"] = present_sections / len(required_sections)
        
        return validation
    
    def validate_concepts(self, concepts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate extracted concepts"""
        validation = {
            "is_valid": True,
            "total_concepts": len(concepts),
            "high_confidence_concepts": 0,
            "warnings": []
        }
        
        for concept in concepts:
            confidence = concept.get("confidence", 0)
            if confidence >= 0.8:
                validation["high_confidence_concepts"] += 1
            elif confidence < 0.5:
                validation["warnings"].append(f"Low confidence concept: {concept.get('text', 'unknown')}")
        
        if validation["total_concepts"] == 0:
            validation["warnings"].append("No medical concepts extracted")
        
        return validation
    
    def validate_icd_codes(self, icd_codes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate ICD-10 codes"""
        validation = {
            "is_valid": True,
            "total_codes": len(icd_codes),
            "high_confidence_codes": 0,
            "warnings": []
        }
        
        for code_info in icd_codes:
            confidence = code_info.get("confidence_score", 0)
            if confidence >= 0.8:
                validation["high_confidence_codes"] += 1
            elif confidence < 0.6:
                validation["warnings"].append(f"Low confidence ICD code: {code_info.get('icd10_code', 'unknown')}")
        
        if validation["total_codes"] == 0:
            validation["warnings"].append("No ICD-10 codes suggested")
        
        return validation
    
    def format_to_fhir(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data to FHIR-compatible structure"""
        fhir_document = {
            "resourceType": "Composition",
            "id": f"clinical-note-{int(datetime.now().timestamp())}",
            "status": "final",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "11506-3",
                    "display": "Progress note"
                }]
            },
            "date": datetime.now().isoformat(),
            "title": "Clinical Progress Note",
            "section": []
        }
        
        # Add SOAP sections
        soap_notes = data.get("soap_notes", {})
        soap_section_mappings = {
            "subjective": {"code": "10164-2", "display": "History of present illness"},
            "objective": {"code": "10210-3", "display": "Physical examination"},
            "assessment": {"code": "51847-2", "display": "Evaluation and management"},
            "plan": {"code": "18776-5", "display": "Plan of care"}
        }
        
        for section_name, section_text in soap_notes.items():
            if section_text and section_name in soap_section_mappings:
                mapping = soap_section_mappings[section_name]
                fhir_section = {
                    "title": section_name.capitalize(),
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": mapping["code"],
                            "display": mapping["display"]
                        }]
                    },
                    "text": {
                        "status": "generated",
                        "div": f"<div>{section_text}</div>"
                    }
                }
                fhir_document["section"].append(fhir_section)
        
        # Add concepts as observations
        concepts = data.get("concepts", [])
        if concepts:
            concept_section = {
                "title": "Clinical Concepts",
                "text": {
                    "status": "generated",
                    "div": "<div>Extracted clinical concepts and measurements</div>"
                },
                "entry": []
            }
            
            for concept in concepts[:10]:  # Limit to top 10 concepts
                concept_entry = {
                    "reference": f"Observation/concept-{concept.get('text', '').replace(' ', '-')}",
                    "display": concept.get("text", ""),
                    "category": concept.get("category", "unknown"),
                    "confidence": concept.get("confidence", 0)
                }
                concept_section["entry"].append(concept_entry)
            
            fhir_document["section"].append(concept_section)
        
        # Add ICD codes as conditions
        icd_codes = data.get("icd_codes", [])
        if icd_codes:
            condition_section = {
                "title": "Conditions",
                "text": {
                    "status": "generated",
                    "div": "<div>Identified conditions with ICD-10 codes</div>"
                },
                "entry": []
            }
            
            for icd_info in icd_codes[:5]:  # Limit to top 5 codes
                condition_entry = {
                    "reference": f"Condition/condition-{icd_info.get('icd10_code', '')}",
                    "display": icd_info.get("description", ""),
                    "code": icd_info.get("icd10_code", ""),
                    "confidence": icd_info.get("confidence_score", 0)
                }
                condition_section["entry"].append(condition_entry)
            
            fhir_document["section"].append(condition_section)
        
        return fhir_document
    
    def format_to_hl7(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data to HL7-compatible structure"""
        hl7_document = {
            "message_type": "ORU^R01",
            "timestamp": datetime.now().isoformat(),
            "patient_id": "PATIENT_123",  # Placeholder
            "document_id": f"DOC_{int(datetime.now().timestamp())}",
            "segments": []
        }
        
        # MSH segment
        msh_segment = {
            "segment_type": "MSH",
            "sending_application": "DocuScribe_AI",
            "receiving_application": "EHR_System",
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S")
        }
        hl7_document["segments"].append(msh_segment)
        
        # OBX segments for SOAP notes
        soap_notes = data.get("soap_notes", {})
        for i, (section, content) in enumerate(soap_notes.items(), 1):
            obx_segment = {
                "segment_type": "OBX",
                "set_id": str(i),
                "value_type": "TX",
                "observation_id": f"SOAP_{section.upper()}",
                "observation_value": content,
                "units": "",
                "reference_range": "",
                "abnormal_flags": "",
                "probability": "",
                "nature_of_abnormal_test": "",
                "observation_result_status": "F"
            }
            hl7_document["segments"].append(obx_segment)
        
        return hl7_document
    
    def format_to_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data to structured JSON"""
        json_document = {
            "document_type": "clinical_note",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "metadata": data.get("metadata", {}),
            "clinical_data": {
                "soap_notes": data.get("soap_notes", {}),
                "medical_concepts": data.get("concepts", []),
                "icd10_codes": data.get("icd_codes", [])
            },
            "validation": data.get("validation_results", {}),
            "processing_metrics": {
                "total_concepts": len(data.get("concepts", [])),
                "total_icd_codes": len(data.get("icd_codes", [])),
                "soap_completeness": data.get("validation_results", {}).get("soap_notes", {}).get("completeness_score", 0)
            }
        }
        
        return json_document
    
    def format_to_xml(self, data: Dict[str, Any]) -> str:
        """Format data to XML structure"""
        xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
        xml_content += '<clinical_document>\n'
        xml_content += f'  <metadata>\n'
        xml_content += f'    <generated_at>{datetime.now().isoformat()}</generated_at>\n'
        xml_content += f'    <version>1.0</version>\n'
        xml_content += f'  </metadata>\n'
        
        # SOAP Notes
        xml_content += '  <soap_notes>\n'
        soap_notes = data.get("soap_notes", {})
        for section, content in soap_notes.items():
            xml_content += f'    <{section}><![CDATA[{content}]]></{section}>\n'
        xml_content += '  </soap_notes>\n'
        
        # Medical Concepts
        xml_content += '  <medical_concepts>\n'
        concepts = data.get("concepts", [])
        for concept in concepts:
            xml_content += '    <concept>\n'
            xml_content += f'      <text>{concept.get("text", "")}</text>\n'
            xml_content += f'      <category>{concept.get("category", "")}</category>\n'
            xml_content += f'      <confidence>{concept.get("confidence", 0)}</confidence>\n'
            xml_content += '    </concept>\n'
        xml_content += '  </medical_concepts>\n'
        
        # ICD Codes
        xml_content += '  <icd10_codes>\n'
        icd_codes = data.get("icd_codes", [])
        for icd in icd_codes:
            xml_content += '    <icd_code>\n'
            xml_content += f'      <code>{icd.get("icd10_code", "")}</code>\n'
            xml_content += f'      <description><![CDATA[{icd.get("description", "")}]]></description>\n'
            xml_content += f'      <confidence>{icd.get("confidence_score", 0)}</confidence>\n'
            xml_content += '    </icd_code>\n'
        xml_content += '  </icd10_codes>\n'
        
        xml_content += '</clinical_document>'
        
        return {"xml_content": xml_content}
    
    def format_to_text(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data to human-readable text"""
        text_content = "CLINICAL DOCUMENTATION SUMMARY\n"
        text_content += "=" * 50 + "\n\n"
        text_content += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # SOAP Notes
        soap_notes = data.get("soap_notes", {})
        if soap_notes:
            text_content += "SOAP NOTES:\n"
            text_content += "-" * 20 + "\n\n"
            
            for section, content in soap_notes.items():
                text_content += f"{section.upper()}:\n"
                text_content += f"{content}\n\n"
        
        # Medical Concepts
        concepts = data.get("concepts", [])
        if concepts:
            text_content += "EXTRACTED MEDICAL CONCEPTS:\n"
            text_content += "-" * 30 + "\n\n"
            
            for concept in concepts[:10]:
                text_content += f"• {concept.get('text', '')} "
                text_content += f"({concept.get('category', '')}, "
                text_content += f"confidence: {concept.get('confidence', 0):.2f})\n"
            text_content += "\n"
        
        # ICD Codes
        icd_codes = data.get("icd_codes", [])
        if icd_codes:
            text_content += "SUGGESTED ICD-10 CODES:\n"
            text_content += "-" * 25 + "\n\n"
            
            for icd in icd_codes[:5]:
                text_content += f"• {icd.get('icd10_code', '')}: "
                text_content += f"{icd.get('description', '')} "
                text_content += f"(confidence: {icd.get('confidence_score', 0):.2f})\n"
            text_content += "\n"
        
        # Validation Summary
        validation = data.get("validation_results", {})
        if validation:
            text_content += "VALIDATION SUMMARY:\n"
            text_content += "-" * 20 + "\n\n"
            
            soap_val = validation.get("soap_notes", {})
            text_content += f"SOAP Notes Completeness: {soap_val.get('completeness_score', 0):.1%}\n"
            
            concepts_val = validation.get("concepts", {})
            text_content += f"Medical Concepts Found: {concepts_val.get('total_concepts', 0)}\n"
            
            icd_val = validation.get("icd_codes", {})
            text_content += f"ICD-10 Codes Suggested: {icd_val.get('total_codes', 0)}\n"
        
        return {"text_content": text_content}
    
    def add_output_metadata(self, formatted_output: Dict[str, Any], 
                          output_format: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata and validation information to the output"""
        final_output = {
            "format": output_format,
            "generated_at": datetime.now().isoformat(),
            "generator": "DocuScribe_AI_v1.0",
            "data": formatted_output,
            "metadata": {
                "processing_info": metadata,
                "format_info": {
                    "target_format": output_format,
                    "is_ehr_ready": output_format.lower() in ["fhir", "hl7"],
                    "human_readable": output_format.lower() == "text"
                }
            }
        }
        
        # Add validation status
        if "validation_results" in formatted_output:
            final_output["validation_status"] = self.summarize_validation(formatted_output["validation_results"])
        
        return final_output
    
    def summarize_validation(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize validation results"""
        summary = {
            "overall_status": "valid",
            "warnings": [],
            "errors": [],
            "completeness_score": 0.0
        }
        
        # Check SOAP validation
        soap_val = validation_results.get("soap_notes", {})
        if not soap_val.get("is_valid", True):
            summary["overall_status"] = "invalid"
            summary["errors"].extend(soap_val.get("missing_sections", []))
        summary["warnings"].extend(soap_val.get("warnings", []))
        summary["completeness_score"] = soap_val.get("completeness_score", 0)
        
        # Check concepts validation
        concepts_val = validation_results.get("concepts", {})
        summary["warnings"].extend(concepts_val.get("warnings", []))
        
        # Check ICD validation
        icd_val = validation_results.get("icd_codes", {})
        summary["warnings"].extend(icd_val.get("warnings", []))
        
        return summary
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback result when formatting fails"""
        return {
            "format": "error",
            "generated_at": datetime.now().isoformat(),
            "generator": "DocuScribe_AI_v1.0",
            "data": {
                "error": "Output formatting failed",
                "message": "Unable to format clinical data due to technical error"
            },
            "metadata": {
                "processing_info": {},
                "format_info": {
                    "target_format": "error",
                    "is_ehr_ready": False,
                    "human_readable": True
                }
            }
        }
