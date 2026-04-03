import React, { useState, useEffect } from 'react';
import { MapPin, Search, Navigation } from 'lucide-react';
import { searchLocations } from '../services/api';

const LocationSelector = ({ onLocationSelect, currentLocation }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    const searchTimer = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        setIsSearching(true);
        try {
          const data = await searchLocations(searchQuery);
          setSuggestions(data.locations || []);
        } catch (err) {
          console.error('Search error:', err);
          setSuggestions([]);
        }
        setIsSearching(false);
      } else {
        setSuggestions([]);
      }
    }, 300);

    return () => clearTimeout(searchTimer);
  }, [searchQuery]);

  const handleUseCurrentLocation = () => {
    if ('geolocation' in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          onLocationSelect({
            name: 'Current Location',
            lat: position.coords.latitude,
            lon: position.coords.longitude,
          });
          setShowSuggestions(false);
        },
        (error) => {
          alert('Unable to get your location. Please search for a city.');
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  const handleSelectLocation = (location) => {
    onLocationSelect(location);
    setSearchQuery(location.name);
    setShowSuggestions(false);
  };

  return (
    <div className="location-selector">
      <div className="search-container">
        <Search size={20} className="search-icon" />
        <input
          type="text"
          placeholder="Search for a city..."
          value={searchQuery}
          onChange={(e) => {
            setSearchQuery(e.target.value);
            setShowSuggestions(true);
          }}
          onFocus={() => setShowSuggestions(true)}
        />
        <button
          className="current-location-btn"
          onClick={handleUseCurrentLocation}
          title="Use current location"
        >
          <Navigation size={20} />
        </button>
      </div>

      {showSuggestions && (suggestions.length > 0 || isSearching) && (
        <div className="suggestions-dropdown">
          {isSearching ? (
            <div className="suggestion-loading">Searching...</div>
          ) : (
            suggestions.map((location, index) => (
              <button
                key={index}
                className="suggestion-item"
                onClick={() => handleSelectLocation(location)}
              >
                <MapPin size={16} />
                <span>{location.name}</span>
              </button>
            ))
          )}
        </div>
      )}

      {currentLocation && (
        <div className="current-selection">
          <MapPin size={16} />
          <span>{currentLocation.name}</span>
        </div>
      )}
    </div>
  );
};

export default LocationSelector;
