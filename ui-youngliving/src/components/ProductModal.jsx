import React from 'react';

export function ProductModal({ product, onClose }) {
  if (!product) return null;

  const { producto, nombreBotanico, dosisDifusor, dilucionV6, precauciones, modoEmpleo } = product;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <div className="modal-header-title">
            <span className="modal-icon">🌿</span>
            <div>
              <h3>{producto}</h3>
              {nombreBotanico && <p className="modal-sub">{nombreBotanico}</p>}
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </header>

        <div className="modal-body">
          <div className="modal-grid">
            <div className="modal-card-item">
              <span className="label">💨 Dosis Difusor</span>
              <p className="value">{dosisDifusor || 'Consultar recomendación general'}</p>
            </div>

            <div className="modal-card-item">
              <span className="label">🧪 Dilución Aceite V-6</span>
              <p className="value">{dilucionV6 || 'Uso según sensibilidad de la piel'}</p>
            </div>
          </div>

          {modoEmpleo && (
            <div className="modal-section">
              <h4>🎯 Modo de Empleo</h4>
              <p>{modoEmpleo}</p>
            </div>
          )}

          {precauciones && (
            <div className="modal-section warning-box">
              <h4>⚠️ Precauciones y Advertencias</h4>
              <p>{precauciones}</p>
            </div>
          )}
        </div>

        <footer className="modal-footer">
          <button className="btn-secondary" onClick={onClose}>Cerrar Ficha</button>
        </footer>
      </div>
    </div>
  );
}
