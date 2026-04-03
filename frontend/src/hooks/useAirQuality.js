import { useState, useEffect, useCallback } from 'react';
import { getAirQuality, getPredictions } from '../services/api';

export const useAirQuality = (latitude, longitude) => {
  const [currentAqi, setCurrentAqi] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    if (!latitude || !longitude) return;

    setLoading(true);
    setError(null);

    try {
      // Fetch current AQI and predictions in parallel
      const [aqiData, predictionData] = await Promise.all([
        getAirQuality(latitude, longitude),
        getPredictions(latitude, longitude, 24),
      ]);

      setCurrentAqi(aqiData);
      setPredictions(predictionData.predictions || []);
    } catch (err) {
      console.error('Error fetching air quality data:', err);
      setError(err.message || 'Failed to fetch air quality data');
    } finally {
      setLoading(false);
    }
  }, [latitude, longitude]);

  useEffect(() => {
    fetchData();
    
    // Refresh data every 10 minutes
    const interval = setInterval(fetchData, 10 * 60 * 1000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return {
    currentAqi,
    predictions,
    loading,
    error,
    refetch: fetchData,
  };
};
