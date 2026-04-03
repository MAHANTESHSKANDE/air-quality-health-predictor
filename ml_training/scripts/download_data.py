"""
Script to download historical air quality data for model training.
Run this script before training the models.
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cities to collect data from (varied pollution levels)
CITIES = [
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
    {"name": "Los_Angeles", "lat": 34.0522, "lon": -118.2437},
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
]


def fetch_city_data(city: dict, days: int = 90) -> pd.DataFrame:
    """Fetch historical AQI data for a city."""
    print(f"Fetching data for {city['name']}...")
    
    base_url = "[api.openaq.org](https://api.openaq.org/v2/measurements)"
    all_data = []
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Fetch data in chunks (API limit)
    for param in ["pm25", "pm10", "no2", "o3", "co"]:
        try:
            response = requests.get(
                base_url,
                params={
                    "coordinates": f"{city['lat']},{city['lon']}",
                    "radius": 50000,  # 50km radius
                    "date_from": start_date.strftime("%Y-%m-%d"),
                    "date_to": end_date.strftime("%Y-%m-%d"),
                    "parameter": param,
                    "limit": 10000,
                },
                timeout=60
            )
            response.raise_for_status()
            
            results = response.json().get("results", [])
            
            for r in results:
                all_data.append({
                    "city": city["name"],
                    "latitude": city["lat"],
                    "longitude": city["lon"],
                    "parameter": r.get("parameter"),
                    "value": r.get("value"),
                    "unit": r.get("unit"),
                    "datetime": r.get("date", {}).get("utc"),
                    "location": r.get("location")
                })
            
            print(f"  - {param}: {len(results)} measurements")
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"  - Error fetching {param}: {e}")
    
    return pd.DataFrame(all_data)


def main():
    print("=" * 60)
    print("Air Quality Data Download Script")
    print("=" * 60)
    
    all_city_data = []
    
    for city in CITIES:
        city_df = fetch_city_data(city)
        if not city_df.empty:
            all_city_data.append(city_df)
        print()
    
    if all_city_data:
        combined_df = pd.concat(all_city_data, ignore_index=True)
        
        # Save to CSV
        output_path = os.path.join(OUTPUT_DIR, "air_quality_raw.csv")
        combined_df.to_csv(output_path, index=False)
        
        print("=" * 60)
        print(f"Downloaded {len(combined_df)} total measurements")
        print(f"Saved to: {output_path}")
        print("=" * 60)
    else:
        print("No data downloaded. Check your internet connection.")


if __name__ == "__main__":
    main()
