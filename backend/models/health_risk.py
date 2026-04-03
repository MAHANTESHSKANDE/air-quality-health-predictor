import joblib
import os
from config import Config

class HealthRiskCalculator:
    """Calculate personalized health risk based on AQI and user health profile."""
    
    # Risk multipliers for different health conditions
    CONDITION_MULTIPLIERS = {
        "asthma": 2.5,
        "copd": 3.0,
        "heart_disease": 2.0,
        "diabetes": 1.5,
        "respiratory_infection": 2.0,
        "pregnancy": 1.8,
        "elderly": 1.7,  # Age > 65
        "child": 1.6,    # Age < 12
        "outdoor_worker": 1.5,
        "smoker": 1.8
    }
    
    # Activity risk factors
    ACTIVITY_MULTIPLIERS = {
        "resting": 1.0,
        "light_activity": 1.3,
        "moderate_exercise": 2.0,
        "vigorous_exercise": 3.0
    }
    
    def __init__(self):
        self.ml_model = None
        self._load_model()
    
    def _load_model(self):
        """Load trained health risk model if available."""
        try:
            if os.path.exists(Config.HEALTH_MODEL_PATH):
                self.ml_model = joblib.load(Config.HEALTH_MODEL_PATH)
                print("Health risk model loaded")
        except Exception as e:
            print(f"Could not load health risk model: {e}")
    
    def calculate_risk(self, aqi: int, health_profile: dict) -> dict:
        """
        Calculate personalized health risk score.
        
        Args:
            aqi: Current AQI value
            health_profile: User's health information including:
                - age: int
                - conditions: list of health conditions
                - planned_activity: activity level
                - exposure_duration: hours of outdoor exposure
                
        Returns:
            Dictionary with risk score, level, and recommendations
        """
        # Base risk from AQI
        base_risk = self._aqi_to_base_risk(aqi)
        
        # Calculate multiplier from health conditions
        condition_multiplier = 1.0
        conditions = health_profile.get("conditions", [])
        
        for condition in conditions:
            condition_lower = condition.lower().replace(" ", "_")
            if condition_lower in self.CONDITION_MULTIPLIERS:
                # Use maximum multiplier rather than cumulative
                condition_multiplier = max(
                    condition_multiplier, 
                    self.CONDITION_MULTIPLIERS[condition_lower]
                )
        
        # Age-based adjustments
        age = health_profile.get("age", 30)
        if age > 65:
            condition_multiplier = max(condition_multiplier, self.CONDITION_MULTIPLIERS["elderly"])
        elif age < 12:
            condition_multiplier = max(condition_multiplier, self.CONDITION_MULTIPLIERS["child"])
        
        # Activity multiplier
        activity = health_profile.get("planned_activity", "light_activity")
        activity_multiplier = self.ACTIVITY_MULTIPLIERS.get(activity, 1.0)
        
        # Exposure duration factor (risk increases with time)
        exposure_hours = health_profile.get("exposure_duration", 1)
        exposure_factor = 1 + (exposure_hours - 1) * 0.1  # 10% increase per hour
        
        # Calculate final risk score (0-100)
        risk_score = base_risk * condition_multiplier * activity_multiplier * exposure_factor
        risk_score = min(100, max(0, round(risk_score)))
        
        # Determine risk level and get recommendations
        risk_level = self._get_risk_level(risk_score)
        recommendations = self._get_recommendations(aqi, risk_score, health_profile)
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "base_risk": round(base_risk),
            "condition_impact": round((condition_multiplier - 1) * 100),
            "activity_impact": round((activity_multiplier - 1) * 100),
            "recommendations": recommendations,
            "safe_outdoor_hours": self._calculate_safe_hours(aqi, condition_multiplier)
        }
    
    def _aqi_to_base_risk(self, aqi: int) -> float:
        """Convert AQI to base health risk score."""
        if aqi <= 50:
            return aqi * 0.4  # 0-20 risk
        elif aqi <= 100:
            return 20 + (aqi - 50) * 0.4  # 20-40 risk
        elif aqi <= 150:
            return 40 + (aqi - 100) * 0.5  # 40-65 risk
        elif aqi <= 200:
            return 65 + (aqi - 150) * 0.5  # 65-90 risk
        else:
            return min(100, 90 + (aqi - 200) * 0.1)  # 90-100 risk
    
    def _get_risk_level(self, risk_score: int) -> dict:
        """Convert risk score to categorical level."""
        if risk_score < 20:
            return {"level": "Low", "color": "#4caf50"}
        elif risk_score < 40:
            return {"level": "Moderate", "color": "#ffeb3b"}
        elif risk_score < 60:
            return {"level": "High", "color": "#ff9800"}
        elif risk_score < 80:
            return {"level": "Very High", "color": "#f44336"}
        else:
            return {"level": "Severe", "color": "#9c27b0"}
    
    def _get_recommendations(self, aqi: int, risk_score: int, health_profile: dict) -> list:
        """Generate personalized health recommendations."""
        recommendations = []
        conditions = health_profile.get("conditions", [])
        
        # Universal recommendations based on AQI
        if aqi > 100:
            recommendations.append({
                "priority": "high",
                "action": "Limit outdoor activities",
                "reason": "Air quality is unhealthy for sensitive groups"
            })
        
        if aqi > 150:
            recommendations.append({
                "priority": "high",
                "action": "Wear an N95 mask outdoors",
                "reason": "Particles in the air can penetrate deep into lungs"
            })
            recommendations.append({
                "priority": "high",
                "action": "Keep windows closed",
                "reason": "Prevent outdoor pollution from entering your home"
            })
        
        if aqi > 200:
            recommendations.append({
                "priority": "urgent",
                "action": "Stay indoors if possible",
                "reason": "Air quality is unhealthy for everyone"
            })
            recommendations.append({
                "priority": "high",
                "action": "Run air purifier if available",
                "reason": "HEPA filters can remove harmful particles"
            })
        
        # Condition-specific recommendations
        if "asthma" in [c.lower() for c in conditions]:
            recommendations.append({
                "priority": "high",
                "action": "Keep rescue inhaler accessible",
                "reason": "Air pollution can trigger asthma symptoms"
            })
            if aqi > 100:
                recommendations.append({
                    "priority": "high",
                    "action": "Consider preventive inhaler use",
                    "reason": "Pre-treatment can reduce symptom severity"
                })
        
        if "heart_disease" in [c.lower().replace(" ", "_") for c in conditions]:
            recommendations.append({
                "priority": "medium",
                "action": "Monitor for chest discomfort or fatigue",
                "reason": "Air pollution increases cardiovascular stress"
            })
        
        # Activity-based recommendations
        activity = health_profile.get("planned_activity", "")
        if activity in ["moderate_exercise", "vigorous_exercise"] and aqi > 100:
            recommendations.append({
                "priority": "high",
                "action": "Move exercise indoors or reduce intensity",
                "reason": "Heavy breathing increases pollutant intake significantly"
            })
        
        # General wellness recommendations
        if risk_score > 30:
            recommendations.append({
                "priority": "medium",
                "action": "Stay hydrated",
                "reason": "Helps body clear inhaled pollutants"
            })
        
        return recommendations
    
    def _calculate_safe_hours(self, aqi: int, condition_multiplier: float) -> float:
        """Estimate safe outdoor exposure hours."""
        if aqi <= 50:
            base_hours = 8.0
        elif aqi <= 100:
            base_hours = 4.0
        elif aqi <= 150:
            base_hours = 2.0
        elif aqi <= 200:
            base_hours = 1.0
        else:
            base_hours = 0.5
        
        # Reduce based on health conditions
        safe_hours = base_hours / condition_multiplier
        return round(max(0.25, safe_hours), 1)
