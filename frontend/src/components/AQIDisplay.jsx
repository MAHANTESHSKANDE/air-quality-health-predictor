import React from 'react';
import { Wind, Droplets, AlertCircle } from 'lucide-react';
import { getAqiCategory, POLLUTANT_INFO } from '../utils/constants';

const AQIDisplay = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="aqi-display loading">
        <div className="spinner"></div>
        <p>Loading air quality data...</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="aqi-display empty">
        <AlertCircle size={48} />
        <p>Select a location to see air quality data</p>
      </div>
    );
  }

  const category = getAqiCategory(data.aqi);

  return (
    <div className="aqi-display" style={{ borderColor: category.color }}>
      <div className="aqi-main">
        <div className="aqi-value" style={{ color: category.color }}>
          {data.aqi}
        </div>
        <div className="aqi-label">
          <span className="category-emoji">{category.emoji}</span>
          <span className="category-label">{category.label}</span>
        </div>
      </div>

      <div className="aqi-location">
        {data.location?.name && (
          <p className="station-name">
            📍 {data.location.name}
            {data.location.city && `, ${data.location.city}`}
          </p>
        )}
        <p className="timestamp">
          Updated: {new Date(data.timestamp).toLocaleTimeString()}
        </p>
        {data.isFallback && (
          <p className="fallback-notice">⚠️ Using estimated data</p>
        )}
      </div>

      <div className="pollutants-grid">
        {Object.entries(data.pollutants || {}).map(([key, pollutant]) => {
          const info = POLLUTANT_INFO[key] || { name: key, unit: '' };
          return (
            <div key={key} className="pollutant-card">
              <div className="pollutant-icon">
                {key.includes('pm') ? <Droplets size={20} /> : <Wind size={20} />}
              </div>
              <div className="pollutant-info">
                <span className="pollutant-name">{info.name}</span>
                <span className="pollutant-value">
                  {typeof pollutant.value === 'number' 
                    ? pollutant.value.toFixed(1) 
                    : pollutant.value}
                  <span className="pollutant-unit">{pollutant.unit || info.unit}</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AQIDisplay;
