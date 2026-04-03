import numpy as np
from datetime import datetime

class DataProcessor:
    """Utility class for data processing and validation."""
    
    @staticmethod
    def validate_coordinates(latitude: float, longitude: float) -> bool:
        """Validate geographic coordinates."""
        if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            return False
        if latitude < -90 or latitude > 90:
            return False
        if longitude < -180 or longitude > 180:
            return False
        return True
    
    @staticmethod
    def validate_health_profile(profile: dict) -> tuple:
        """
        Validate and sanitize health profile data.
        
        Returns:
            (is_valid, sanitized_profile or error_message)
        """
        sanitized = {}
        
        # Age validation
        age = profile.get("age")
        if age is not None:
            try:
                age = int(age)
                if age < 0 or age > 120:
                    return False, "Age must be between 0 and 120"
                sanitized["age"] = age
            except (ValueError, TypeError):
                return False, "Invalid age format"
        else:
            sanitized["age"] = 30  # Default age
        
        # Conditions validation
        conditions = profile.get("conditions", [])
        if not isinstance(conditions, list):
            return False, "Conditions must be a list"
        valid_conditions = [
            "asthma", "copd", "heart disease", "diabetes",
            "respiratory infection", "pregnancy", "smoker"
        ]
        sanitized["conditions"] = [
            c for c in conditions 
            if isinstance(c, str) and c.lower() in valid_conditions
        ]
        
        # Activity validation
        activity = profile.get("planned_activity", "light_activity")
        valid_activities = ["resting", "light_activity", "moderate_exercise", "vigorous_exercise"]
        if activity not in valid_activities:
            activity = "light_activity"
        sanitized["planned_activity"] = activity
        
        # Exposure duration validation
        exposure = profile.get("exposure_duration", 1)
        try:
            exposure = float(exposure)
            exposure = max(0.5, min(24, exposure))
        except (ValueError, TypeError):
            exposure = 1.0
        sanitized["exposure_duration"] = exposure
        
        return True, sanitized
    
    @staticmethod
    def format_aqi_response(raw_data: dict) -> dict:
        """Format AQI data for frontend consumption."""
        return {
            "aqi": raw_data.get("aqi", 0),
            "category": raw_data.get("category", {}),
            "pollutants": raw_data.get("pollutants", {}),
            "location": raw_data.get("station", {}),
            "timestamp": raw_data.get("timestamp", datetime.utcnow().isoformat()),
            "isFallback": raw_data.get("is_fallback", False)
        }
