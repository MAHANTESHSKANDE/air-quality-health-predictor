import React, { useState, useEffect } from 'react';
import { RefreshCw, AlertCircle } from 'lucide-react';
import LocationSelector from './LocationSelector';
import AQIDisplay from './AQIDisplay';
import PredictionChart from './PredictionChart';
import HealthProfile from './HealthProfile';
import HealthRiskCard from './HealthRiskCard';
import { useAirQuality } from '../hooks/useAirQuality';
import { useHealthRisk } from '../hooks/useHealthRisk';

const Dashboard = () => {
  const [location, setLocation] = useState(null);
  const { currentAqi, predictions, loading, error, refetch } = useAirQuality(
    location?.lat,
    location?.lon
  );
  const { riskData, loading: riskLoading, calculate: calculateRisk } = useHealthRisk();

  const handleLocationSelect = (newLocation) => {
    setLocation(newLocation);
  };

  const handleHealthProfileSubmit = async (profile) => {
    if (currentAqi?.aqi) {
      await calculateRisk(currentAqi.aqi, profile);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>🌍 Air Quality & Health Monitor</h1>
        <p className="subtitle">Real-time air quality with personalized health recommendations</p>
      </header>

      <div className="dashboard-controls">
        <LocationSelector
          onLocationSelect={handleLocationSelect}
          currentLocation={location}
        />
        {location && (
          <button className="refresh-btn" onClick={refetch} disabled={loading}>
            <RefreshCw size={18} className={loading ? 'spinning' : ''} />
            {loading ? 'Loading...' : 'Refresh'}
          </button>
        )}
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={20} />
          <span>{error}</span>
          <button onClick={refetch}>Retry</button>
        </div>
      )}

      <div className="dashboard-grid">
        <div className="grid-left">
          <AQIDisplay data={currentAqi} loading={loading || !location} />
          <PredictionChart predictions={predictions} loading={loading || !location} />
        </div>
        <div className="grid-right">
          <HealthProfile onSubmit={handleHealthProfileSubmit} loading={riskLoading} />
          <HealthRiskCard riskData={riskData} loading={riskLoading} />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;