import React from 'react';
import { Shield, Clock, AlertTriangle } from 'lucide-react';

const HealthRiskCard = ({ riskData, loading }) => {
  if (loading) {
    return (
      <div className="health-risk-card loading">
        <div className="spinner"></div>
        <p>Calculating your personalized risk...</p>
      </div>
    );
  }

  if (!riskData) {
    return null;
  }

  const { risk_assessment } = riskData;
  const { risk_score, risk_level, recommendations, safe_outdoor_hours } = risk_assessment;

  return (
    <div className="health-risk-card" style={{ borderColor: risk_level.color }}>
      <div className="risk-header">
        <Shield size={32} style={{ color: risk_level.color }} />
        <div className="risk-score-display">
          <span className="risk-score" style={{ color: risk_level.color }}>
            {risk_score}
          </span>
          <span className="risk-label">{risk_level.level} Risk</span>
        </div>
      </div>

      <div className="risk-details">
        <div className="detail-item">
          <Clock size={18} />
          <span>
            Safe outdoor time: <strong>{safe_outdoor_hours} hours</strong>
          </span>
        </div>
      </div>

      {recommendations && recommendations.length > 0 && (
        <div className="recommendations">
          <h4>
            <AlertTriangle size={18} /> Recommendations
          </h4>
          <ul>
            {recommendations.slice(0, 5).map((rec, index) => (
              <li
                key={index}
                className={`recommendation-item priority-${rec.priority}`}
              >
                <strong>{rec.action}</strong>
                <span className="recommendation-reason">{rec.reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default HealthRiskCard;
