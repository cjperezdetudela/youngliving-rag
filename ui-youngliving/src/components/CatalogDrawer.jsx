import React, { useState, useEffect } from 'react';
import { ProductCard } from './ProductCard';
import { ArticleCard } from './ArticleCard';
import { API_BASE_URL } from '../config';

export function CatalogDrawer({ isOpen, onClose, onSelectProduct, onSelectArticle }) {
  const [products, setProducts] = useState([]);
  const [articles, setArticles] = useState([]);
  const [stats, setStats] = useState({ totalProducts: 30, totalArticles: 72, totalReferences: 102 });

  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('ALL'); // ALL, PRODUCTS, ARTICLES
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      fetch(`${API_BASE_URL}/api/catalog`)
        .then((res) => res.json())
        .then((data) => {
          setProducts(data.products || []);
          setArticles(data.articles || []);
          setStats({
            totalProducts: data.totalProducts || 30,
            totalArticles: data.totalArticles || 72,
            totalReferences: data.totalReferences || 102
          });
        })
        .catch((err) => console.error("Error al cargar catálogo:", err))
        .finally(() => setIsLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const queryNorm = searchQuery.toLowerCase().trim();

  const filteredProducts = products.filter((p) => {
    if (!queryNorm) return true;
    return (
      p.producto.toLowerCase().includes(queryNorm) ||
      p.nombreBotanico.toLowerCase().includes(queryNorm) ||
      p.modoEmpleo.toLowerCase().includes(queryNorm)
    );
  });

  const filteredArticles = articles.filter((a) => {
    if (!queryNorm) return true;
    return (
      a.title.toLowerCase().includes(queryNorm) ||
      a.category.toLowerCase().includes(queryNorm) ||
      a.description.toLowerCase().includes(queryNorm) ||
      a.tags.toLowerCase().includes(queryNorm)
    );
  });

  return (
    <div className="drawer-overlay" onClick={onClose}>
      <div className="drawer-container drawer-container-wide" onClick={(e) => e.stopPropagation()}>
        <header className="drawer-header">
          <div>
            <h2>📖 Base de Conocimiento Young Living ({stats.totalReferences} Referencias)</h2>
            <p>{stats.totalProducts} Fichas Técnicas del Vademécum + {stats.totalArticles} Artículos y Guías del Blog</p>
          </div>
          <button className="drawer-close-btn" onClick={onClose}>✕</button>
        </header>

        <div className="drawer-search-bar">
          <input
            type="text"
            placeholder="Buscar entre 102 aceites, recetas, usos o guías..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="drawer-filters">
            <button
              className={`filter-btn ${activeTab === 'ALL' ? 'active' : ''}`}
              onClick={() => setActiveTab('ALL')}
            >
              ✨ Todo ({filteredProducts.length + filteredArticles.length})
            </button>
            <button
              className={`filter-btn ${activeTab === 'PRODUCTS' ? 'active' : ''}`}
              onClick={() => setActiveTab('PRODUCTS')}
            >
              🌱 Fichas Vademécum ({filteredProducts.length})
            </button>
            <button
              className={`filter-btn ${activeTab === 'ARTICLES' ? 'active' : ''}`}
              onClick={() => setActiveTab('ARTICLES')}
            >
              📰 Artículos Blog ({filteredArticles.length})
            </button>
          </div>
        </div>

        <div className="drawer-content">
          {isLoading ? (
            <div className="loading-spinner">Cargando base de conocimiento...</div>
          ) : (
            <div className="drawer-sections-wrapper">
              {(activeTab === 'ALL' || activeTab === 'PRODUCTS') && filteredProducts.length > 0 && (
                <section className="drawer-section">
                  <h3 className="section-title">🌱 Fichas Técnicas del Vademécum ({filteredProducts.length})</h3>
                  <div className="catalog-grid">
                    {filteredProducts.map((prod, idx) => (
                      <ProductCard key={`p-${idx}`} product={prod} onSelect={onSelectProduct} />
                    ))}
                  </div>
                </section>
              )}

              {(activeTab === 'ALL' || activeTab === 'ARTICLES') && filteredArticles.length > 0 && (
                <section className="drawer-section" style={{ marginTop: '24px' }}>
                  <h3 className="section-title">📰 Artículos y Guías del Blog ({filteredArticles.length})</h3>
                  <div className="catalog-grid">
                    {filteredArticles.map((art, idx) => (
                      <ArticleCard key={`a-${idx}`} article={art} onSelect={onSelectArticle} />
                    ))}
                  </div>
                </section>
              )}

              {filteredProducts.length === 0 && filteredArticles.length === 0 && (
                <div className="empty-catalog">
                  No se encontraron referencias ni artículos que coincidan con "{searchQuery}".
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
