export const AQI_CATEGORIES = {
  GOOD: { min: 0, max: 50, label: 'Good', color: '#00e400', emoji: '😊' },
  MODERATE: { min: 51, max: 100, label: 'Moderate', color: '#ffff00', emoji: '🙂' },
  UNHEALTHY_SENSITIVE: { min: 101, max: 150, label: 'Unhealthy for Sensitive Groups', color: '#ff7e00', emoji: '😐' },
  UNHEALTHY: { min: 151, max: 200, label: 'Unhealthy', color: '#ff0000', emoji: '😷' },
  VERY_UNHEALTHY: { min: 201, max: 300, label: 'Very Unhealthy', color: '#8f3f97', emoji: '🤢' },
  HAZARDOUS: { min: 301, max: 500, label: 'Hazardous', color: '#7e0023', emoji: '☠️' },
};

export const HEALTH_CONDITIONS = [
  { id: 'asthma', label: 'Asthma' },
  { id: 'copd', label: 'COPD' },
  { id: 'heart_disease', label: 'Heart Disease' },
  { id: 'diabetes', label: 'Diabetes' },
  { id: 'respiratory_infection', label: 'Respiratory Infection' },
  { id: 'pregnancy', label: 'Pregnancy' },
  { id: 'smoker', label: 'Smoker' },
];

export const ACTIVITY_LEVELS = [
  { id: 'resting', label: 'Resting / Indoors' },
  { id: 'light_activity', label: 'Light Activity (walking)' },
  { id: 'moderate_exercise', label: 'Moderate Exercise (jogging)' },
  { id: 'vigorous_exercise', label: 'Vigorous Exercise (running, sports)' },
];

export const POLLUTANT_INFO = {
  pm25: { name: 'PM2.5', unit: 'µg/m³', description: 'Fine particulate matter' },
  pm10: { name: 'PM10', unit: 'µg/m³', description: 'Coarse particulate matter' },
  no2: { name: 'NO₂', unit: 'ppb', description: 'Nitrogen dioxide' },
  o3: { name: 'O₃', unit: 'ppb', description: 'Ozone' },
  co: { name: 'CO', unit: 'ppm', description: 'Carbon monoxide' },
  so2: { name: 'SO₂', unit: 'ppb', description: 'Sulfur dioxide' },
};

export const getAqiCategory = (aqi) => {
  for (const category of Object.values(AQI_CATEGORIES)) {
    if (aqi >= category.min && aqi <= category.max) {
      return category;
    }
  }
  return AQI_CATEGORIES.HAZARDOUS;
};
