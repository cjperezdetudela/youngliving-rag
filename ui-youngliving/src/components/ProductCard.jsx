import React from 'react';

export function ProductCard({ product, onSelect }) {
  if (!product) return null;

  const { producto, nombreBotanico, dosisDifusor, dilucionV6 } = product;

  return (
    <div className="interactive-product-card" onClick={() => onSelect && onSelect(product)}>
      <div className="product-card-header">
        <div className="product-icon">💧</div>
        <div className="product-title-group">
          <h4 className="product-name">{producto}</h4>
          {nombreBotanico && <span className="botanical-name">{nombreBotanico}</span>}
        </div>
      </div>

      <div className="product-badges">
        {dosisDifusor && (
          <span className="badge badge-diffuser" title="Dosis recomendada para difusor">
            💨 {dosisDifusor}
          </span>
        )}
        {dilucionV6 && (
          <span className="badge badge-v6" title="Recomendación de dilución en V-6">
            🧪 {dilucionV6}
          </span>
        )}
      </div>

      <div className="product-card-footer">
        <span className="action-link">Ver Ficha Técnica Completa →</span>
      </div>
    </div>
  );
}
