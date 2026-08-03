import React from 'react';

const PRESET_QUERIES = [
  { icon: '🌿', label: 'Dosis difusor Lavanda y Menta', query: '¿Cuál es la dosis recomendada para difusor de lavanda y menta?' },
  { icon: '🛡️', label: 'Dilución Thieves con V-6', query: '¿Cómo debo diluir la mezcla Thieves con aceite vegetal V-6?' },
  { icon: '👶', label: 'Precauciones en bebés y embarazadas', query: '¿Qué precauciones de seguridad debo tener en embarazadas o bebés?' },
  { icon: '🍋', label: 'Aceite de Limón y fotosensibilidad', query: '¿Cuáles son los usos y precauciones de fotosensibilidad del aceite de limón?' }
];

export function PresetChips({ onSelectQuery }) {
  return (
    <div className="preset-chips-container">
      <span className="preset-title">Sugerencias rápidas:</span>
      <div className="preset-chips-scroll">
        {PRESET_QUERIES.map((item, idx) => (
          <button
            key={idx}
            className="preset-chip-btn"
            onClick={() => onSelectQuery(item.query)}
          >
            <span className="chip-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
