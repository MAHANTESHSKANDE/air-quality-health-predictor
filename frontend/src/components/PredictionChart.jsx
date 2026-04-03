import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';
import { getAqiCategory } from '../utils/constants';

const PredictionChart = ({ predictions, loading }) => {
  if (loading || !predictions || predictions.length === 0) {
    return (
      <div className="prediction-chart loading">
        <p>{loading ? 'Loading predictions...' : 'No predictions available'}</p>
      </div>
    );
  }

  // Format data for chart
  const chartData = predictions.map((pred) => ({
    hour: new Date(pred.timestamp).getHours(),
    time: new Date(pred.timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    }),
    aqi: pred.predicted_aqi,
    confidence: pred.confidence,
    category: pred.category?.level || 'Unknown',
    color: pred.category?.color || '#999',
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="chart-tooltip">
          <p className="tooltip-time">{data.time}</p>
          <p className="tooltip-aqi" style={{ color: data.color }}>
            AQI: {data.aqi}
          </p>
          <p className="tooltip-category">{data.category}</p>
          <p className="tooltip-confidence">Confidence: {data.confidence}%</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="prediction-chart">
      <h3>24-Hour AQI Forecast</h3>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="aqiGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8884d8" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#8884d8" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#eee" />
          <XAxis
            dataKey="time"
            tick={{ fontSize: 12 }}
            interval={2}
            tickLine={false}
          />
          <YAxis
            domain={[0, 'dataMax + 50']}
            tick={{ fontSize: 12 }}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip content={<CustomTooltip />} />
          
          {/* Reference lines for AQI categories */}
          <ReferenceLine y={50} stroke="#00e400" strokeDasharray="5 5" />
          <ReferenceLine y={100} stroke="#ffff00" strokeDasharray="5 5" />
          <ReferenceLine y={150} stroke="#ff7e00" strokeDasharray="5 5" />
          
          <Area
            type="monotone"
            dataKey="aqi"
            stroke="none"
            fill="url(#aqiGradient)"
          />
          <Line
            type="monotone"
            dataKey="aqi"
            stroke="#8884d8"
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: '#8884d8' }}
          />
        </ComposedChart>
      </ResponsiveContainer>
      
      <div className="chart-legend">
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#00e400' }}></span>
          Good (&lt;50)
        </span>
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ffff00' }}></span>
          Moderate (51-100)
        </span>
        <span className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ff7e00' }}></span>
          Unhealthy (101-150)
        </span>
      </div>
    </div>
  );
};

export default PredictionChart;
