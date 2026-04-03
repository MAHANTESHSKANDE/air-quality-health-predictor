import numpy as np
import joblib
import os
from datetime import datetime, timedelta
from config import Config

class PredictionService:
    """Service to make AQI predictions using trained ML models."""
    
    def __init__(self):
        self.aqi_model = None
        self.scaler = None
        self._load_models()
    
    def _load_models(self):
        """Load trained models from disk."""
        try:
            if os.path.exists(Config.AQI_MODEL_PATH):
                self.aqi_model = joblib.load(Config.AQI_MODEL_PATH)
                print("AQI forecasting model loaded successfully")
            else:
                print("AQI model not found, using fallback predictions")
                
            if os.path.exists(Config.SCALER_PATH):
                self.scaler = joblib.load(Config.SCALER_PATH)
                print("Scaler loaded successfully")
                
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def predict_next_hours(self, current_aqi: float, pollutants: dict, hours: int = 24):
        """
        Predict AQI values for the next N hours.
        
        Args:
            current_aqi: Current AQI value
            pollutants: Current pollutant measurements
            hours: Number of hours to predict (default 24)
            
        Returns:
            List of predictions with timestamps
        """
        predictions = []
        current_time = datetime.utcnow()
        
        # Extract features from current data
        pm25 = pollutants.get("pm25", {}).get("value", 25)
        pm10 = pollutants.get("pm10", {}).get("value", 50)
        no2 = pollutants.get("no2", {}).get("value", 20)
        o3 = pollutants.get("o3", {}).get("value", 40)
        
        for hour in range(1, hours + 1):
            prediction_time = current_time + timedelta(hours=hour)
            
            if self.aqi_model is not None:
                # Use trained model
                features = self._create_features(
                    current_aqi, pm25, pm10, no2, o3,
                    prediction_time.hour, prediction_time.weekday()
                )
                
                if self.scaler:
                    features = self.scaler.transform([features])
                else:
                    features = [features]
                    
                predicted_aqi = self.aqi_model.predict(features)[0]
            else:
                # Fallback: simple persistence with time-of-day adjustment
                predicted_aqi = self._fallback_prediction(current_aqi, prediction_time.hour, hour)
            
            # Ensure AQI is within valid range
            predicted_aqi = max(0, min(500, round(predicted_aqi)))
            
            predictions.append({
                "timestamp": prediction_time.isoformat(),
                "hour": prediction_time.hour,
                "predicted_aqi": predicted_aqi,
                "category": self._get_category(predicted_aqi),
                "confidence": self._calculate_confidence(hour)
            })
        
        return predictions
    
    def _create_features(self, aqi, pm25, pm10, no2, o3, hour, weekday):
        """Create feature vector for model input."""
        # Cyclical encoding for hour
        hour_sin = np.sin(2 * np.pi * hour / 24)
        hour_cos = np.cos(2 * np.pi * hour / 24)
        
        # Weekend flag
        is_weekend = 1 if weekday >= 5 else 0
        
        # Rush hour flag (7-9 AM and 5-7 PM)
        is_rush_hour = 1 if hour in [7, 8, 9, 17, 18, 19] else 0
        
        return [aqi, pm25, pm10, no2, o3, hour_sin, hour_cos, is_weekend, is_rush_hour]
    
    def _fallback_prediction(self, current_aqi, target_hour, hours_ahead):
        """Simple fallback prediction when model isn't available."""
        # Time-of-day multipliers (pollution typically higher during rush hours)
        hour_factors = {
            0: 0.7, 1: 0.65, 2: 0.6, 3: 0.55, 4: 0.55, 5: 0.6,
            6: 0.75, 7: 0.9, 8: 1.1, 9: 1.15, 10: 1.1, 11: 1.0,
            12: 0.95, 13: 0.9, 14: 0.85, 15: 0.9, 16: 1.0, 17: 1.15,
            18: 1.2, 19: 1.1, 20: 1.0, 21: 0.9, 22: 0.8, 23: 0.75
        }
        
        factor = hour_factors.get(target_hour, 1.0)
        
        # Add some randomness and decay based on hours ahead
        noise = np.random.normal(0, 5)
        decay = 0.98 ** hours_ahead
        
        return current_aqi * factor * decay + noise
    
    def _get_category(self, aqi):
        """Get category for predicted AQI."""
        for (low, high), info in Config.AQI_CATEGORIES.items():
            if low <= aqi <= high:
                return info
        return {"level": "Hazardous", "color": "#7e0023", "risk": 6}
    
    def _calculate_confidence(self, hours_ahead):
        """Calculate prediction confidence (decreases with time)."""
        # Confidence drops roughly 2% per hour
        base_confidence = 95
        confidence = base_confidence - (hours_ahead * 2)
        return max(50, round(confidence))
