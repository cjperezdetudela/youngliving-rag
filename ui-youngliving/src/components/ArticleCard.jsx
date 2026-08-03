import React from 'react';

export function ArticleCard({ article, onSelect }) {
  if (!article) return null;

  const { title, category, date, description } = article;

  return (
    <div className="interactive-article-card" onClick={() => onSelect && onSelect(article)}>
      <div className="article-card-header">
        <span className="article-category-badge">{category || 'BLOG'}</span>
        {date && <span className="article-date">{date}</span>}
      </div>

      <h4 className="article-title">{title}</h4>
      {description && <p className="article-description">{description.slice(0, 110)}...</p>}

      <div className="article-card-footer">
        <span className="action-link">Leer Artículo Completo →</span>
      </div>
    </div>
  );
}
