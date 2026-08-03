import { useState } from 'react';

export function AuthModal({ isOpen, onClose, onLoginSuccess, initialTab = 'login' }) {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password || (activeTab === 'register' && !name)) {
      setErrorMsg('Por favor completa todos los campos obligatorios.');
      return;
    }

    // Simulate successful login / registration
    const userData = {
      name: name.trim() || email.split('@')[0] || 'Miembro Bienestar',
      email: email,
      avatar: '🌿',
      isMember: true,
      memberSince: '2026'
    };

    setErrorMsg('');
    onLoginSuccess(userData);
    onClose();
  };

  const handleQuickDemo = () => {
    const demoUser = {
      name: 'Usuario Invitado',
      email: 'invitado@youngliving-rag.com',
      avatar: '💧',
      isMember: false
    };
    onLoginSuccess(demoUser);
    onClose();
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="auth-modal-card" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>✕</button>

        <div className="auth-header">
          <div className="auth-brand-logo">🌿</div>
          <h2>{activeTab === 'login' ? 'Bienvenido de Nuevo' : 'Únete a la Comunidad'}</h2>
          <p className="auth-subtitle">
            {activeTab === 'login'
              ? 'Ingresa tus credenciales para acceder a tu Asesor Personal de Bienestar'
              : 'Crea tu cuenta para guardar tus mezclas favoritas y consultas personalizadas'}
          </p>
        </div>

        <div className="auth-tabs">
          <button
            className={`auth-tab ${activeTab === 'login' ? 'active' : ''}`}
            onClick={() => { setActiveTab('login'); setErrorMsg(''); }}
          >
            Iniciar Sesión
          </button>
          <button
            className={`auth-tab ${activeTab === 'register' ? 'active' : ''}`}
            onClick={() => { setActiveTab('register'); setErrorMsg(''); }}
          >
            Crear Cuenta
          </button>
        </div>

        {errorMsg && <div className="auth-error-alert">⚠️ {errorMsg}</div>}

        <form onSubmit={handleSubmit} className="auth-form">
          {activeTab === 'register' && (
            <div className="form-group">
              <label htmlFor="name-input">Nombre Completo</label>

              <input
                id="name-input"
                type="text"
                placeholder="Ej. María Carmen Ruiz"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email-input">Correo Electrónico</label>

            <input
              id="email-input"
              type="email"
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="pass-input">Contraseña</label>

            <input
              id="pass-input"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {activeTab === 'login' && (
            <div className="form-extra">
              <label className="remember-checkbox">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                />
                <span>Recordarme en este dispositivo</span>
              </label>
              <a href="#forgot" className="forgot-link" onClick={(e) => e.preventDefault()}>
                ¿Olvidaste tu contraseña?
              </a>
            </div>
          )}

          <button type="submit" className="auth-submit-btn">
            {activeTab === 'login' ? 'Acceder al Asesor 🌿' : 'Registrarme y Comenzar ✨'}
          </button>
        </form>

        <div className="auth-divider">
          <span>O ACCEDE RÁPIDAMENTE</span>
        </div>

        <button className="auth-demo-btn" onClick={handleQuickDemo}>
          💧 Continuar como Invitado (Acceso Demo)
        </button>

        <p className="auth-footer-text">
          Al continuar, aceptas nuestros términos de servicio de consulta de aromaterapia y política de privacidad.
        </p>
      </div>
    </div>
  );
}
