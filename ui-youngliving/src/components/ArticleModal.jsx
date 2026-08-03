import React from 'react';

export function ArticleModal({ article, onClose }) {
  if (!article) return null;

  const { title, category, date, fullText, url, tags } = article;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container modal-container-large" onClick={(e) => e.stopPropagation()}>
        <header className="modal-header">
          <div className="modal-header-title">
            <span className="modal-icon">📰</span>
            <div>
              <h3>{title}</h3>
              <p className="modal-sub">{category} • {date}</p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>✕</button>
        </header>

        <div className="modal-body">
          {tags && (
            <div className="article-tags-chips">
              {tags.split(',').map((t, idx) => (
                <span key={idx} className="chip">{t.trim()}</span>
              ))}
            </div>
          )}

          <div className="article-full-content">
            {fullText ? (
              fullText.split('\n').map((para, i) => (
                para.trim() ? <p key={i}>{para}</p> : <div key={i} className="spacer" />
              ))
            ) : (
              <p>No hay contenido completo disponible para este artículo.</p>
            )}
          </div>
        </div>

        <footer className="modal-footer" style={{ justifyContent: 'space-between' }}>
          {url ? (
            <a href={url} target="_blank" rel="noopener noreferrer" className="action-link" style={{ fontSize: '0.9rem' }}>
              🌐 Ver en la web oficial de Young Living →
            </a>
          ) : <div />}
          <button className="btn-secondary" onClick={onClose}>Cerrar Artículo</button>
        </footer>
      </div>
    </div>
  );
}
