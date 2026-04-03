import { useState, useCallback } from 'react';
import { calculateHealthRisk } from '../services/api';

export const useHealthRisk = () => {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const calculate = useCallback(async (aqi, healthProfile) => {
    if (!aqi || !healthProfile) return;

    setLoading(true);
    setError(null);

    try {
      const data = await calculateHealthRisk(aqi, healthProfile);
      setRiskData(data);
      return data;
    } catch (err) {
      console.error('Error calculating health risk:', err);
      setError(err.message || 'Failed to calculate health risk');
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearRisk = useCallback(() => {
    setRiskData(null);
    setError(null);
  }, []);

  return {
    riskData,
    loading,
    error,
    calculate,
    clearRisk,
  };
};
