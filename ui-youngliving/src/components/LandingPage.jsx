export function LandingPage({ onOpenAuth, onStartChat, user, onLogout }) {
  return (
    <div className="landing-container">
      {/* Decorative ambient background glows */}
      <div className="glow-orb orb-1"></div>
      <div className="glow-orb orb-2"></div>
      <div className="glow-orb orb-3"></div>

      {/* Navigation Header */}
      <header className="landing-header">
        <div className="landing-logo">
          <span className="logo-icon">🌿</span>
          <div className="logo-text">
            <span className="brand-name">Young Living</span>
            <span className="brand-sub">Asesor de Bienestar IA</span>
          </div>
        </div>

        <nav className="landing-nav">
          <a href="#caracteristicas">Características</a>
          <a href="#seguridad">Seguridad</a>
          <a href="#beneficios">Beneficios</a>
        </nav>

        <div className="landing-header-actions">
          {user ? (
            <div className="user-profile-badge">
              <span className="user-avatar">{user.avatar}</span>
              <span className="user-name">{user.name}</span>
              <button className="btn-chat-primary" onClick={onStartChat}>
                Ir al Asesor 💬
              </button>
              <button className="btn-logout" onClick={onLogout} title="Cerrar Sesión">
                🚪
              </button>
            </div>
          ) : (
            <>
              <button className="btn-login-ghost" onClick={() => onOpenAuth('login')}>
                Iniciar Sesión
              </button>
              <button className="btn-register-primary" onClick={() => onOpenAuth('register')}>
                Registrarse ✨
              </button>
            </>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <div className="hero-pill">
            <span className="pill-pulse"></span>
            <span>Inteligencia Artificial aplicada a la Aromaterapia</span>
          </div>

          <h1 className="hero-title">
            Descubre el Poder Natural de los <span className="text-gradient">Aceites Esenciales</span>
          </h1>

          <p className="hero-subtitle">
            Tu asistente privado respaldado por inteligencia artificial para consultas sobre aromaterapia, mezclas para difusor y uso seguro de aceites esenciales.
          </p>

          <div className="hero-cta-group">
            {user ? (
              <button className="cta-btn-main" onClick={onStartChat}>
                <span>Iniciar Consulta con IA</span>
                <span className="btn-arrow">→</span>
              </button>
            ) : (
              <>
                <button className="cta-btn-main" onClick={() => onOpenAuth('login')}>
                  <span>Acceso Miembros / Iniciar Sesión</span>
                  <span className="btn-arrow">→</span>
                </button>
                <button className="cta-btn-secondary" onClick={onStartChat}>
                  <span>Explorar como Invitado</span>
                </button>
              </>
            )}
          </div>

          <div className="hero-trust-badges">
            <div className="trust-item">
              <span className="trust-num">IA 2.5</span>
              <span className="trust-label">Google Gemini</span>
            </div>
            <div className="trust-divider"></div>
            <div className="trust-item">
              <span className="trust-num">100%</span>
              <span className="trust-label">Uso Seguro V-6</span>
            </div>
            <div className="trust-divider"></div>
            <div className="trust-item">
              <span className="trust-num">Respuestas</span>
              <span className="trust-label">Verificadas</span>
            </div>
          </div>
        </div>

        {/* Hero Interactive Card Preview */}
        <div className="hero-preview-wrapper">
          <div className="glass-preview-card">
            <div className="card-top-bar">
              <span className="badge-live">⚡ RAG Live Engine</span>
              <span className="model-tag">Gemini 2.5 Flash</span>
            </div>

            <div className="preview-chat-sample">
              <div className="sample-msg user">
                <p>¿Qué aceite me recomiendas para relajarme por la noche y cómo debo aplicarlo?</p>
              </div>

              <div className="sample-msg assistant">
                <div className="assistant-avatar">🌿</div>
                <div className="sample-text">
                  <p>Te recomiendo el <strong>Aceite Esencial de Lavender (Lavanda)</strong> o la mezcla <strong>Stress Away</strong>.</p>
                  
                  <div className="sample-product-chip">
                    <span className="chip-icon">💧</span>
                    <div>
                      <strong>Lavandula angustifolia</strong>
                      <small>Difusor: 4-6 gotas | Dilución V-6: 1 gota por 5ml</small>
                    </div>
                  </div>

                  <p className="sample-footnote">
                    <i>Precaución: Evitar contacto directo con los ojos. Aplicar en sienes y plantas de los pies.</i>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="caracteristicas" className="features-section">
        <div className="section-header">
          <span className="section-tag">ASISTENCIA INTELIGENTE</span>
          <h2>Todo lo que necesitas para tu bienestar natural</h2>
        </div>

        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🌿</div>
            <h3>Consultas Personalizadas</h3>
            <p>Obtén respuestas sobre propiedades de aceites, combinaciones y modos de empleo adecuados.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">💡</div>
            <h3>Recetas & Difusor</h3>
            <p>Descubre combinaciones para difusor según el estado de ánimo, la estación del año o la concentración.</p>
          </div>

          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>Asistente IA RAG</h3>
            <p>Respuestas precisas en tiempo real combinando conocimiento experto con razonamiento contextual.</p>
          </div>

          <div className="feature-card" id="seguridad">
            <div className="feature-icon">🛡️</div>
            <h3>Seguridad Garantizada</h3>
            <p>Recomendaciones guiadas por protocolos de seguridad y advertencias para uso tópico o en difusor.</p>
          </div>
        </div>
      </section>

      {/* Footer Banner */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <span>🌿 Young Living Asesor IA</span>
            <p>© 2026 Asesor de Bienestar y Aromaterapia Natural. Todos los derechos reservados.</p>
          </div>
          <div className="footer-links">
            <a href="#asistente" onClick={(e) => { e.preventDefault(); onStartChat(); }}>Probar Asesor</a>
            <a href="#auth" onClick={(e) => { e.preventDefault(); onOpenAuth('login'); }}>Acceder</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
