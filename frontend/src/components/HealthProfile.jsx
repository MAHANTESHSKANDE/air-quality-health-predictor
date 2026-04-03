import React, { useState } from 'react';
import { User, Activity, Clock } from 'lucide-react';
import { HEALTH_CONDITIONS, ACTIVITY_LEVELS } from '../utils/constants';

const HealthProfile = ({ onSubmit, loading }) => {
  const [profile, setProfile] = useState({
    age: 30,
    conditions: [],
    planned_activity: 'light_activity',
    exposure_duration: 2,
  });

  const handleConditionToggle = (conditionId) => {
    setProfile((prev) => ({
      ...prev,
      conditions: prev.conditions.includes(conditionId)
        ? prev.conditions.filter((c) => c !== conditionId)
        : [...prev.conditions, conditionId],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(profile);
  };

  return (
    <form className="health-profile-form" onSubmit={handleSubmit}>
      <h3>
        <User size={20} /> Your Health Profile
      </h3>

      <div className="form-group">
        <label htmlFor="age">Age</label>
        <input
          type="number"
          id="age"
          min="1"
          max="120"
          value={profile.age}
          onChange={(e) =>
            setProfile((prev) => ({ ...prev, age: parseInt(e.target.value) || 30 }))
          }
        />
      </div>

      <div className="form-group">
        <label>Health Conditions</label>
        <div className="conditions-grid">
          {HEALTH_CONDITIONS.map((condition) => (
            <button
              key={condition.id}
              type="button"
              className={`condition-btn ${
                profile.conditions.includes(condition.id) ? 'selected' : ''
              }`}
              onClick={() => handleConditionToggle(condition.id)}
            >
              {condition.label}
            </button>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label>
          <Activity size={16} /> Planned Outdoor Activity
        </label>
        <select
          value={profile.planned_activity}
          onChange={(e) =>
            setProfile((prev) => ({ ...prev, planned_activity: e.target.value }))
          }
        >
          {ACTIVITY_LEVELS.map((level) => (
            <option key={level.id} value={level.id}>
              {level.label}
            </option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>
          <Clock size={16} /> Planned Exposure Duration: {profile.exposure_duration} hours
        </label>
        <input
          type="range"
          min="0.5"
          max="8"
          step="0.5"
          value={profile.exposure_duration}
          onChange={(e) =>
            setProfile((prev) => ({
              ...prev,
              exposure_duration: parseFloat(e.target.value),
            }))
          }
        />
      </div>

      <button type="submit" className="submit-btn" disabled={loading}>
        {loading ? 'Calculating...' : 'Calculate My Risk'}
      </button>
    </form>
  );
};

export default HealthProfile;
