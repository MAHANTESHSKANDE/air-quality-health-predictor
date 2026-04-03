import requests
from datetime import datetime, timedelta
from config import Config

class AirQualityService:
    def __init__(self):
        self.base_url = Config.OPENAQ_BASE_URL
        self.headers = {}
        if Config.OPENAQ_API_KEY:
            self.headers["Authorization"] = f"Bearer {Config.OPENAQ_API_KEY}"
    
    def get_current_aqi(self, latitude: float, longitude: float, radius: int = 25000):
        try:
            response = requests.get(
                f"{self.base_url}/latest",
                params={
                    "coordinates": f"{latitude},{longitude}",
                    "radius": radius,
                    "limit": 100,
                },
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("results"):
                return self._get_fallback_data(latitude, longitude)
            
            return self._process_measurements(data["results"])
            
        except requests.RequestException as e:
            print(f"Error fetching AQI data: {e}")
            return self._get_fallback_data(latitude, longitude)
    
    def _process_measurements(self, results):
        pollutants = {}
        station_info = None
        
        for result in results[:10]:  # Take top 10 closest stations
            if not station_info and result.get("location"):
                station_info = {
                    "name": result["location"].get("coordinates", "Unknown Station"),
                    "city": result.get("city", "Unknown"),
                    "country": result.get("country", "Unknown")
                }
            
            for measurement in result.get("measurements", []):
                param = measurement.get("parameter")
                value = measurement.get("value")
                unit = measurement.get("unit", "µg/m³")
                
                if param and value is not None:
                    pollutants[param] = {
                        "value": value,
                        "unit": unit,
                        "lastUpdated": measurement.get("date", {}).get("utc")
                    }
        
        aqi = self._calculate_aqi(pollutants)
        category = self._get_aqi_category(aqi)
        
        return {
            "aqi": round(aqi),
            "category": category,
            "pollutants": pollutants,
            "station": station_info,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_aqi(self, pollutants):
        pm25 = pollutants.get("pm25", {}).get("value")
        if pm25 is None:
            pm10 = pollutants.get("pm10", {}).get("value")
            if pm10:
                return self._pm10_to_aqi(pm10)
            return 50
        return self._pm25_to_aqi(pm25)
    
    def _pm25_to_aqi(self, concentration):
        breakpoints = [
            (0.0, 12.0, 0, 50), (12.1, 35.4, 51, 100),
            (35.5, 55.4, 101, 150), (55.5, 150.4, 151, 200),
            (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400),
            (350.5, 500.4, 401, 500)
        ]
        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
            if bp_lo <= concentration <= bp_hi:
                return ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
        return 500 if concentration > 500.4 else 0
    
    def _pm10_to_aqi(self, concentration):
        breakpoints = [
            (0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
            (255, 354, 151, 200), (355, 424, 201, 300), (425, 504, 301, 400),
            (505, 604, 401, 500)
        ]
        for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
            if bp_lo <= concentration <= bp_hi:
                return ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (concentration - bp_lo) + aqi_lo
        return 500 if concentration > 604 else 0
    
    def _get_aqi_category(self, aqi):
        for (low, high), info in Config.AQI_CATEGORIES.items():
            if low <= aqi <= high:
                return info
        return {"level": "Hazardous", "color": "#7e0023", "risk": 6}
    
    def _get_fallback_data(self, latitude, longitude):
        return {
            "aqi": 75,
            "category": {"level": "Moderate", "color": "#ffff00", "risk": 2},
            "pollutants": {
                "pm25": {"value": 22.5, "unit": "µg/m³"},
                "pm10": {"value": 45.0, "unit": "µg/m³"},
                "no2": {"value": 25.0, "unit": "µg/m³"},
                "o3": {"value": 60.0, "unit": "µg/m³"}
            },
            "station": {"name": "Estimated Data", "city": "Your Location"},
            "timestamp": datetime.utcnow().isoformat(),
            "is_fallback": True
        }