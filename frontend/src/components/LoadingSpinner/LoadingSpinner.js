import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ message = 'Analyzing URL...', subtext = 'Please wait while we perform security checks' }) => {
  return (
    <div className="loading-spinner-container">
      <div className="spinner-wrapper">
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-ring"></div>
        <div className="spinner-center"></div>
      </div>
      
      <div className="loading-text">{message}</div>
      <div className="loading-subtext">{subtext}</div>
      
      <div className="loading-progress">
        <div className="progress-bar"></div>
      </div>
      
      <div className="scanning-animation">
        <div className="scan-dot"></div>
        <div className="scan-dot"></div>
        <div className="scan-dot"></div>
      </div>
    </div>
  );
};

export default LoadingSpinner;



