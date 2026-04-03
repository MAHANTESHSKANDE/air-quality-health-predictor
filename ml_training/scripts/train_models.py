"""
Script to train AQI forecasting and health risk models.
Run after downloading data with download_data.py.
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "raw", "air_quality_raw.csv")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
MODEL_OUTPUT_DIR = os.path.join(SCRIPT_DIR, "..", "..", "backend", "trained_models")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODEL_OUTPUT_DIR, exist_ok=True)


def load_and_preprocess_data():
    """Load raw data and prepare it for training."""
    print("Loading data...")
    
    # Check if real data exists, otherwise generate synthetic
    if os.path.exists(RAW_DATA_PATH):
        df = pd.read_csv(RAW_DATA_PATH)
        df["datetime"] = pd.to_datetime(df["datetime"])
    else:
        print("Raw data not found. Generating synthetic training data...")
        df = generate_synthetic_data()
    
    print(f"Loaded {len(df)} records")
    return df


def generate_synthetic_data(n_samples=50000):
    """Generate synthetic air quality data for training."""
    np.random.seed(42)
    
    dates = pd.date_range(
        start="2023-01-01",
        end="2024-01-01",
        periods=n_samples
    )
    
    data = []
    for dt in dates:
        hour = dt.hour
        weekday = dt.weekday()
        month = dt.month
        
        # Base PM2.5 with seasonal and daily patterns
        base_pm25 = 30
        
        # Seasonal effect (higher in winter)
        seasonal = 20 * np.sin(2 * np.pi * (month - 1) / 12)
        
        # Rush hour effect
        if hour in [7, 8, 9, 17, 18, 19]:
            rush_hour = 15
        else:
            rush_hour = 0
        
        # Weekend effect (lower on weekends)
        weekend = -10 if weekday >= 5 else 0
        
        # Random variation
        noise = np.random.normal(0, 10)
        
        pm25 = max(5, base_pm25 + seasonal + rush_hour + weekend + noise)
        pm10 = pm25 * 1.8 + np.random.normal(0, 5)
        no2 = 20 + 0.3 * pm25 + np.random.normal(0, 5)
        o3 = 50 - 0.2 * pm25 + np.random.normal(0, 10)
        
        data.append({
            "datetime": dt,
            "city": np.random.choice(["Delhi", "Beijing", "LA", "London"]),
            "parameter": "pm25",
            "value": pm25,
            "pm10": max(5, pm10),
            "no2": max(0, no2),
            "o3": max(0, o3),
        })
    
    return pd.DataFrame(data)


def create_features(df):
    """Create feature matrix for model training."""
    print("Creating features...")
    
    # If data has separate parameter rows, pivot it
    if "parameter" in df.columns and df["parameter"].nunique() > 1:
        # Group by datetime and pivot
        pivot_df = df.pivot_table(
            index=["datetime", "city"],
            columns="parameter",
            values="value",
            aggfunc="mean"
        ).reset_index()
        df = pivot_df
    
    # Ensure we have datetime features
    df["hour"] = df["datetime"].dt.hour
    df["weekday"] = df["datetime"].dt.weekday
    df["month"] = df["datetime"].dt.month
    df["day_of_year"] = df["datetime"].dt.dayofyear
    
    # Cyclical encoding
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    
    # Binary features
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)
    df["is_rush_hour"] = df["hour"].isin([7, 8, 9, 17, 18, 19]).astype(int)
    
    return df


def calculate_aqi_from_pm25(pm25):
    """Convert PM2.5 to AQI."""
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]
    
    for bp_lo, bp_hi, aqi_lo, aqi_hi in breakpoints:
        if bp_lo <= pm25 <= bp_hi:
            return ((aqi_hi - aqi_lo) / (bp_hi - bp_lo)) * (pm25 - bp_lo) + aqi_lo
    return 500 if pm25 > 500.4 else 0


def train_aqi_forecasting_model(df):
    """Train model to predict future AQI values."""
    print("\n" + "=" * 60)
    print("Training AQI Forecasting Model")
    print("=" * 60)
    
    # Create target variable (next hour's PM2.5 / AQI)
    df = df.sort_values("datetime")
    
    # Get PM2.5 column (might have different names)
    pm25_col = None
    for col in ["pm25", "value", "PM2.5"]:
        if col in df.columns:
            pm25_col = col
            break
    
    if pm25_col is None:
        print("No PM2.5 data found")
        return None, None
    
    df["current_pm25"] = df[pm25_col]
    df["target_aqi"] = df[pm25_col].shift(-1).apply(
        lambda x: calculate_aqi_from_pm25(x) if pd.notna(x) else np.nan
    )
    
    # Remove rows with NaN target
    df = df.dropna(subset=["target_aqi"])
    
    # Select features
    feature_cols = [
        "current_pm25", "hour_sin", "hour_cos", 
        "month_sin", "month_cos", "is_weekend", "is_rush_hour"
    ]
    
    # Add pollutant features if available
    for col in ["pm10", "no2", "o3"]:
        if col in df.columns:
            feature_cols.append(col)
    
    # Ensure all feature columns exist
    available_features = [col for col in feature_cols if col in df.columns]
    
    X = df[available_features].fillna(0)
    y = df["target_aqi"]
    
    print(f"Training samples: {len(X)}")
    print(f"Features: {available_features}")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1
    )
    
    print("Training model...")
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nModel Performance:")
    print(f"  MAE:  {mae:.2f} AQI points")
    print(f"  RMSE: {rmse:.2f} AQI points")
    print(f"  R²:   {r2:.3f}")
    
    # Feature importance
    print(f"\nFeature Importance:")
    importance = pd.DataFrame({
        "feature": available_features,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)
    print(importance.to_string(index=False))
    
    return model, scaler


def train_health_risk_model():
    """Train model for health risk classification."""
    print("\n" + "=" * 60)
    print("Training Health Risk Classification Model")
    print("=" * 60)
    
    # Generate synthetic health risk training data
    np.random.seed(42)
    n_samples = 10000
    
    data = []
    for _ in range(n_samples):
        aqi = np.random.randint(0, 400)
        age = np.random.randint(5, 85)
        has_asthma = np.random.choice([0, 1], p=[0.85, 0.15])
        has_heart_disease = np.random.choice([0, 1], p=[0.9, 0.1])
        has_copd = np.random.choice([0, 1], p=[0.95, 0.05])
        activity_level = np.random.choice([0, 1, 2, 3])  # rest, light, moderate, vigorous
        exposure_hours = np.random.uniform(0.5, 8)
        
        # Calculate risk score (simplified version of actual logic)
        base_risk = aqi / 5
        
        # Condition multipliers
        multiplier = 1.0
        if has_asthma:
            multiplier = max(multiplier, 2.5)
        if has_heart_disease:
            multiplier = max(multiplier, 2.0)
        if has_copd:
            multiplier = max(multiplier, 3.0)
        if age > 65 or age < 12:
            multiplier = max(multiplier, 1.7)
        
        # Activity multiplier
        activity_mult = [1.0, 1.3, 2.0, 3.0][activity_level]
        
        risk_score = base_risk * multiplier * activity_mult * (1 + exposure_hours * 0.1)
        risk_score = min(100, risk_score)
        
        # Convert to risk class (0: low, 1: moderate, 2: high, 3: very high, 4: severe)
        if risk_score < 20:
            risk_class = 0
        elif risk_score < 40:
            risk_class = 1
        elif risk_score < 60:
            risk_class = 2
        elif risk_score < 80:
            risk_class = 3
        else:
            risk_class = 4
        
        data.append({
            "aqi": aqi,
            "age": age,
            "has_asthma": has_asthma,
            "has_heart_disease": has_heart_disease,
            "has_copd": has_copd,
            "activity_level": activity_level,
            "exposure_hours": exposure_hours,
            "risk_class": risk_class
        })
    
    df = pd.DataFrame(data)
    
    # Features and target
    feature_cols = ["aqi", "age", "has_asthma", "has_heart_disease", 
                    "has_copd", "activity_level", "exposure_hours"]
    
    X = df[feature_cols]
    y = df["risk_class"]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train Gradient Boosting classifier
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    
    print("Training model...")
    model.fit(X_train, y_train)
    
    # Evaluate
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    
    print(f"\nModel Performance:")
    print(f"  Training accuracy: {train_score:.3f}")
    print(f"  Testing accuracy:  {test_score:.3f}")
    
    return model


def save_models(aqi_model, scaler, health_model):
    """Save trained models to disk."""
    print("\n" + "=" * 60)
    print("Saving Models")
    print("=" * 60)
    
    if aqi_model is not None:
        aqi_path = os.path.join(MODEL_OUTPUT_DIR, "aqi_forecast_model.pkl")
        joblib.dump(aqi_model, aqi_path)
        print(f"  AQI model saved to: {aqi_path}")
    
    if scaler is not None:
        scaler_path = os.path.join(MODEL_OUTPUT_DIR, "scaler.pkl")
        joblib.dump(scaler, scaler_path)
        print(f"  Scaler saved to: {scaler_path}")
    
    if health_model is not None:
        health_path = os.path.join(MODEL_OUTPUT_DIR, "health_risk_model.pkl")
        joblib.dump(health_model, health_path)
        print(f"  Health model saved to: {health_path}")


def main():
    print("=" * 60)
    print("Air Quality Model Training Pipeline")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Load and preprocess data
    df = load_and_preprocess_data()
    df = create_features(df)
    
    # Train models
    aqi_model, scaler = train_aqi_forecasting_model(df)
    health_model = train_health_risk_model()
    
    # Save models
    save_models(aqi_model, scaler, health_model)
    
    print("\n" + "=" * 60)
    print("Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
