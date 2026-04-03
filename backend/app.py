from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import os

# Import after ensuring all files exist
from config import Config
from services.air_quality_service import AirQualityService
from services.prediction_service import PredictionService
from models.health_risk import HealthRiskCalculator
from utils.data_processor import DataProcessor

app = Flask(__name__)
# Fixed CORS for both Vite dev ports
CORS(app, origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173"])

# Initialize services
air_quality_service = AirQualityService()
prediction_service = PredictionService()
health_risk_calculator = HealthRiskCalculator()

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    })

@app.route("/api/air-quality", methods=["GET"])
def get_air_quality():
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        
        if lat is None or lon is None:
            return jsonify({"error": "Missing lat or lon parameter"}), 400
        
        if not DataProcessor.validate_coordinates(lat, lon):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        raw_data = air_quality_service.get_current_aqi(lat, lon)
        formatted_data = DataProcessor.format_aqi_response(raw_data)
        
        return jsonify(formatted_data)
        
    except Exception as e:
        print(f"Error in get_air_quality: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/predict", methods=["GET"])
def get_predictions():
    try:
        lat = request.args.get("lat", type=float)
        lon = request.args.get("lon", type=float)
        hours = request.args.get("hours", default=24, type=int)
        
        if lat is None or lon is None:
            return jsonify({"error": "Missing lat or lon parameter"}), 400
        
        if not DataProcessor.validate_coordinates(lat, lon):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        hours = max(1, min(72, hours))
        
        current_data = air_quality_service.get_current_aqi(lat, lon)
        predictions = prediction_service.predict_next_hours(
            current_data["aqi"],
            current_data["pollutants"],
            hours
        )
        
        return jsonify({
            "current": DataProcessor.format_aqi_response(current_data),
            "predictions": predictions,
            "generated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in get_predictions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/health-risk", methods=["POST"])
def calculate_health_risk():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Request body required"}), 400
        
        aqi = data.get("aqi")
        health_profile = data.get("health_profile", {})
        
        if aqi is None:
            return jsonify({"error": "AQI value required"}), 400
        
        try:
            aqi = int(aqi)
            if aqi < 0 or aqi > 500:
                return jsonify({"error": "AQI must be between 0 and 500"}), 400
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid AQI format"}), 400
        
        is_valid, result = DataProcessor.validate_health_profile(health_profile)
        if not is_valid:
            return jsonify({"error": result}), 400
        
        sanitized_profile = result
        risk_data = health_risk_calculator.calculate_risk(aqi, sanitized_profile)
        
        return jsonify({
            "aqi": aqi,
            "health_profile": sanitized_profile,
            "risk_assessment": risk_data,
            "calculated_at": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        print(f"Error in calculate_health_risk: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/api/locations/search", methods=["GET"])
def search_locations():
    query = request.args.get("q", "")
    
    cities = [
        {"name": "New York, USA", "lat": 40.7128, "lon": -74.0060},
        {"name": "Los Angeles, USA", "lat": 34.0522, "lon": -118.2437},
        {"name": "London, UK", "lat": 51.5074, "lon": -0.1278},
        {"name": "Paris, France", "lat": 48.8566, "lon": 2.3522},
        {"name": "Tokyo, Japan", "lat": 35.6762, "lon": 139.6503},
        {"name": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093},
        {"name": "Mumbai, India", "lat": 19.0760, "lon": 72.8777},
        {"name": "Delhi, India", "lat": 28.6139, "lon": 77.2090},
        {"name": "Beijing, China", "lat": 39.9042, "lon": 116.4074},
        {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    ]
    
    if query:
        query_lower = query.lower()
        results = [c for c in cities if query_lower in c["name"].lower()]
    else:
        results = cities
    
    return jsonify({"locations": results[:10]})

if __name__ == "__main__":
    print("Starting Air Quality Health Predictor API...")
    print("API will be available at http://localhost:5000")
    app.run(debug=True, port=5000, host='0.0.0.0')