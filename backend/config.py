import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    OPENAQ_BASE_URL = "https://api.openaq.org/v2"
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", None)
    
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "trained_models")
    AQI_MODEL_PATH = os.path.join(MODEL_DIR, "aqi_forecast_model.pkl")
    HEALTH_MODEL_PATH = os.path.join(MODEL_DIR, "health_risk_model.pkl")
    SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
    
    AQI_CATEGORIES = {
        (0, 50): {"level": "Good", "color": "#00e400", "risk": 1},
        (51, 100): {"level": "Moderate", "color": "#ffff00", "risk": 2},
        (101, 150): {"level": "Unhealthy for Sensitive Groups", "color": "#ff7e00", "risk": 3},
        (151, 200): {"level": "Unhealthy", "color": "#ff0000", "risk": 4},
        (201, 300): {"level": "Very Unhealthy", "color": "#8f3f97", "risk": 5},
        (301, 500): {"level": "Hazardous", "color": "#7e0023", "risk": 6},
    }