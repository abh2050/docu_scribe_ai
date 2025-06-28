from abc import ABC, abstractmethod
from typing import Any, Dict, List
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all agents in the DocuScribe system"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__class__.__module__}.{name}")
        
    @abstractmethod
    def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data and return results"""
        pass
    
    def log_activity(self, activity: str, data: Dict[str, Any] = None):
        """Log agent activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "activity": activity,
            "data": data or {}
        }
        self.logger.info(json.dumps(log_entry))
    
    def calculate_confidence(self, result: Any) -> float:
        """Calculate confidence score for the result"""
        # Default implementation - agents can override
        return 0.85
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Handle errors gracefully"""
        error_info = {
            "error": str(error),
            "context": context,
            "agent": self.name,
            "timestamp": datetime.now().isoformat()
        }
        self.logger.error(json.dumps(error_info))
        return {
            "success": False,
            "error": error_info,
            "fallback_result": self.get_fallback_result()
        }
    
    def get_fallback_result(self) -> Dict[str, Any]:
        """Provide fallback result when processing fails"""
        return {
            "message": f"Agent {self.name} encountered an error",
            "status": "error"
        }
