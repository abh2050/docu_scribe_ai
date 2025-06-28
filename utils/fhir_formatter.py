from typing import Dict, Any, List
import json
from datetime import datetime
import uuid

class FHIRFormatter:
    """Utility class for formatting clinical data to FHIR-compliant structures"""
    
    def __init__(self):
        self.fhir_version = "4.0.1"
        self.base_url = "http://docuscribe.ai/fhir"
    
    def format_to_fhir(self, clinical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert clinical data to FHIR Bundle format
        
        Args:
            clinical_data: Dictionary containing all clinical information
            
        Returns:
            FHIR Bundle resource
        """
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp,
                "profile": [f"http://hl7.org/fhir/StructureDefinition/Bundle"]
            },
            "type": "document",
            "timestamp": timestamp,
            "entry": []
        }
        
        # Create Composition (main document)
        composition = self.create_composition(clinical_data, timestamp)
        bundle["entry"].append({
            "fullUrl": f"{self.base_url}/Composition/{composition['id']}",
            "resource": composition
        })
        
        # Create Patient resource (placeholder)
        patient = self.create_patient_resource()
        bundle["entry"].append({
            "fullUrl": f"{self.base_url}/Patient/{patient['id']}",
            "resource": patient
        })
        
        # Create Practitioner resource (placeholder)
        practitioner = self.create_practitioner_resource()
        bundle["entry"].append({
            "fullUrl": f"{self.base_url}/Practitioner/{practitioner['id']}",
            "resource": practitioner
        })
        
        # Create Encounter resource
        encounter = self.create_encounter_resource(patient["id"], practitioner["id"], timestamp)
        bundle["entry"].append({
            "fullUrl": f"{self.base_url}/Encounter/{encounter['id']}",
            "resource": encounter
        })
        
        # Create Observation resources for vital signs and measurements
        concepts = clinical_data.get("concepts", [])
        vital_observations = self.create_vital_observations(concepts, patient["id"], encounter["id"], timestamp)
        for observation in vital_observations:
            bundle["entry"].append({
                "fullUrl": f"{self.base_url}/Observation/{observation['id']}",
                "resource": observation
            })
        
        # Create Condition resources for diagnoses
        icd_codes = clinical_data.get("icd_codes", [])
        conditions = self.create_condition_resources(icd_codes, patient["id"], encounter["id"], timestamp)
        for condition in conditions:
            bundle["entry"].append({
                "fullUrl": f"{self.base_url}/Condition/{condition['id']}",
                "resource": condition
            })
        
        # Create MedicationStatement resources
        medication_concepts = [c for c in concepts if c.get("category") in ["medications", "medication_detailed"]]
        medications = self.create_medication_resources(medication_concepts, patient["id"], timestamp)
        for medication in medications:
            bundle["entry"].append({
                "fullUrl": f"{self.base_url}/MedicationStatement/{medication['id']}",
                "resource": medication
            })
        
        return bundle
    
    def create_composition(self, clinical_data: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
        """Create FHIR Composition resource for the clinical document"""
        composition_id = str(uuid.uuid4())
        
        composition = {
            "resourceType": "Composition",
            "id": composition_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp
            },
            "status": "final",
            "type": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "11506-3",
                    "display": "Progress note"
                }]
            },
            "subject": {
                "reference": "Patient/patient-placeholder",
                "display": "Patient"
            },
            "encounter": {
                "reference": "Encounter/encounter-placeholder"
            },
            "date": timestamp,
            "author": [{
                "reference": "Practitioner/practitioner-placeholder",
                "display": "Dr. Physician"
            }],
            "title": "Clinical Progress Note - DocuScribe AI Generated",
            "custodian": {
                "display": "DocuScribe AI System"
            },
            "section": []
        }
        
        # Add SOAP sections
        soap_notes = clinical_data.get("soap_notes", {})
        
        # Subjective section
        if soap_notes.get("subjective"):
            composition["section"].append({
                "title": "Subjective",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "10164-2",
                        "display": "History of present illness Narrative"
                    }]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p>{soap_notes['subjective']}</p></div>"
                }
            })
        
        # Objective section
        if soap_notes.get("objective"):
            composition["section"].append({
                "title": "Objective",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "10210-3",
                        "display": "Physical findings of General status Narrative"
                    }]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p>{soap_notes['objective']}</p></div>"
                }
            })
        
        # Assessment section
        if soap_notes.get("assessment"):
            composition["section"].append({
                "title": "Assessment",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "51847-2",
                        "display": "Evaluation + Plan note"
                    }]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p>{soap_notes['assessment']}</p></div>"
                }
            })
        
        # Plan section
        if soap_notes.get("plan"):
            composition["section"].append({
                "title": "Plan",
                "code": {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "18776-5",
                        "display": "Plan of care note"
                    }]
                },
                "text": {
                    "status": "generated",
                    "div": f"<div xmlns='http://www.w3.org/1999/xhtml'><p>{soap_notes['plan']}</p></div>"
                }
            })
        
        return composition
    
    def create_patient_resource(self) -> Dict[str, Any]:
        """Create placeholder Patient resource"""
        patient_id = "patient-placeholder"
        
        return {
            "resourceType": "Patient",
            "id": patient_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat()
            },
            "identifier": [{
                "use": "usual",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "MR",
                        "display": "Medical record number"
                    }]
                },
                "value": "PATIENT123"
            }],
            "name": [{
                "use": "official",
                "family": "Patient",
                "given": ["Test"]
            }],
            "gender": "unknown",
            "birthDate": "1980-01-01"
        }
    
    def create_practitioner_resource(self) -> Dict[str, Any]:
        """Create placeholder Practitioner resource"""
        practitioner_id = "practitioner-placeholder"
        
        return {
            "resourceType": "Practitioner",
            "id": practitioner_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": datetime.now().isoformat()
            },
            "identifier": [{
                "use": "official",
                "type": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                        "code": "NPI",
                        "display": "National provider identifier"
                    }]
                },
                "value": "1234567890"
            }],
            "name": [{
                "use": "official",
                "family": "Physician",
                "given": ["Dr."],
                "prefix": ["Dr."]
            }]
        }
    
    def create_encounter_resource(self, patient_id: str, practitioner_id: str, timestamp: str) -> Dict[str, Any]:
        """Create Encounter resource"""
        encounter_id = "encounter-placeholder"
        
        return {
            "resourceType": "Encounter",
            "id": encounter_id,
            "meta": {
                "versionId": "1",
                "lastUpdated": timestamp
            },
            "status": "finished",
            "class": {
                "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                "code": "AMB",
                "display": "ambulatory"
            },
            "type": [{
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "185349003",
                    "display": "Encounter for check up"
                }]
            }],
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "participant": [{
                "individual": {
                    "reference": f"Practitioner/{practitioner_id}"
                }
            }],
            "period": {
                "start": timestamp,
                "end": timestamp
            }
        }
    
    def create_vital_observations(self, concepts: List[Dict[str, Any]], 
                                patient_id: str, encounter_id: str, timestamp: str) -> List[Dict[str, Any]]:
        """Create Observation resources for vital signs"""
        observations = []
        
        # Filter vital sign concepts
        vital_concepts = [c for c in concepts if c.get("category") == "vital_measurement"]
        
        for vital in vital_concepts:
            observation_id = str(uuid.uuid4())
            vital_type = vital.get("vital_type", "unknown")
            
            observation = {
                "resourceType": "Observation",
                "id": observation_id,
                "meta": {
                    "versionId": "1",
                    "lastUpdated": timestamp
                },
                "status": "final",
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital Signs"
                    }]
                }],
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "encounter": {
                    "reference": f"Encounter/{encounter_id}"
                },
                "effectiveDateTime": timestamp,
                "valueString": vital.get("text", "")
            }
            
            # Add specific coding based on vital type
            if vital_type == "blood_pressure":
                observation["code"] = {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "85354-9",
                        "display": "Blood pressure panel"
                    }]
                }
                if "systolic" in vital and "diastolic" in vital:
                    observation["component"] = [
                        {
                            "code": {
                                "coding": [{
                                    "system": "http://loinc.org",
                                    "code": "8480-6",
                                    "display": "Systolic blood pressure"
                                }]
                            },
                            "valueQuantity": {
                                "value": vital["systolic"],
                                "unit": "mmHg",
                                "system": "http://unitsofmeasure.org",
                                "code": "mm[Hg]"
                            }
                        },
                        {
                            "code": {
                                "coding": [{
                                    "system": "http://loinc.org",
                                    "code": "8462-4",
                                    "display": "Diastolic blood pressure"
                                }]
                            },
                            "valueQuantity": {
                                "value": vital["diastolic"],
                                "unit": "mmHg",
                                "system": "http://unitsofmeasure.org",
                                "code": "mm[Hg]"
                            }
                        }
                    ]
            elif vital_type == "heart_rate":
                observation["code"] = {
                    "coding": [{
                        "system": "http://loinc.org",
                        "code": "8867-4",
                        "display": "Heart rate"
                    }]
                }
                if "value" in vital:
                    observation["valueQuantity"] = {
                        "value": vital["value"],
                        "unit": "beats/min",
                        "system": "http://unitsofmeasure.org",
                        "code": "/min"
                    }
            
            observations.append(observation)
        
        return observations
    
    def create_condition_resources(self, icd_codes: List[Dict[str, Any]], 
                                 patient_id: str, encounter_id: str, timestamp: str) -> List[Dict[str, Any]]:
        """Create Condition resources for diagnoses"""
        conditions = []
        
        for icd_info in icd_codes[:5]:  # Limit to top 5 conditions
            condition_id = str(uuid.uuid4())
            
            condition = {
                "resourceType": "Condition",
                "id": condition_id,
                "meta": {
                    "versionId": "1",
                    "lastUpdated": timestamp
                },
                "clinicalStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                        "code": "active"
                    }]
                },
                "verificationStatus": {
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                        "code": "provisional"
                    }]
                },
                "category": [{
                    "coding": [{
                        "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                        "code": "encounter-diagnosis",
                        "display": "Encounter Diagnosis"
                    }]
                }],
                "code": {
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10-cm",
                        "code": icd_info.get("icd10_code", ""),
                        "display": icd_info.get("description", "")
                    }]
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "encounter": {
                    "reference": f"Encounter/{encounter_id}"
                },
                "recordedDate": timestamp
            }
            
            # Add confidence as an extension
            if "confidence_score" in icd_info:
                condition["extension"] = [{
                    "url": "http://docuscribe.ai/fhir/StructureDefinition/confidence-score",
                    "valueDecimal": icd_info["confidence_score"]
                }]
            
            conditions.append(condition)
        
        return conditions
    
    def create_medication_resources(self, medication_concepts: List[Dict[str, Any]], 
                                  patient_id: str, timestamp: str) -> List[Dict[str, Any]]:
        """Create MedicationStatement resources"""
        medications = []
        
        for med_concept in medication_concepts[:10]:  # Limit to 10 medications
            medication_id = str(uuid.uuid4())
            
            medication = {
                "resourceType": "MedicationStatement",
                "id": medication_id,
                "meta": {
                    "versionId": "1",
                    "lastUpdated": timestamp
                },
                "status": "active",
                "medicationCodeableConcept": {
                    "text": med_concept.get("text", "")
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                },
                "effectiveDateTime": timestamp
            }
            
            # Add detailed medication information if available
            if med_concept.get("category") == "medication_detailed":
                if "medication_name" in med_concept:
                    medication["medicationCodeableConcept"]["coding"] = [{
                        "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                        "display": med_concept["medication_name"]
                    }]
                
                if "dosage" in med_concept and "unit" in med_concept:
                    medication["dosage"] = [{
                        "text": f"{med_concept['dosage']} {med_concept['unit']} {med_concept.get('frequency', '')}".strip(),
                        "timing": {
                            "repeat": {
                                "frequency": 1,
                                "period": 1,
                                "periodUnit": "d"
                            }
                        },
                        "doseAndRate": [{
                            "doseQuantity": {
                                "value": float(med_concept["dosage"]),
                                "unit": med_concept["unit"]
                            }
                        }]
                    }]
            
            medications.append(medication)
        
        return medications
    
    def validate_fhir_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Basic validation of FHIR resource structure"""
        validation = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        if "resourceType" not in resource:
            validation["is_valid"] = False
            validation["errors"].append("Missing required field: resourceType")
        
        if "id" not in resource:
            validation["warnings"].append("Missing recommended field: id")
        
        # Resource-specific validation
        resource_type = resource.get("resourceType")
        if resource_type == "Patient":
            if "name" not in resource:
                validation["warnings"].append("Patient resource should have name")
        elif resource_type == "Observation":
            if "status" not in resource:
                validation["is_valid"] = False
                validation["errors"].append("Observation must have status")
        
        return validation
