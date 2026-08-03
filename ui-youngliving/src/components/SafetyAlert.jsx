import React from 'react';

export function SafetyAlert({ message }) {
  return (
    <div className="safety-alert">
      <div className="icon">⚠️</div>
      <p>{message}</p>
    </div>
  );
}
