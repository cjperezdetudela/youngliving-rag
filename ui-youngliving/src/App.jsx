import { useState, useRef, useEffect } from 'react';
import './App.css';
import { ChatMessage } from './components/ChatMessage';
import { PresetChips } from './components/PresetChips';
import { ProductModal } from './components/ProductModal';
import { ArticleModal } from './components/ArticleModal';
import { LandingPage } from './components/LandingPage';
import { AuthModal } from './components/AuthModal';
import { API_BASE_URL } from './config';

const INITIAL_CONVERSATION = [
  {
    id: 1,
    role: 'assistant',
    text: '¡Hola! Soy tu **Asesor de Aceites Esenciales y Bienestar**.\n\n¿En qué te puedo ayudar hoy sobre aromaterapia, recetas y uso seguro de aceites?'
  }
];

function App() {
  const [currentView, setCurrentView] = useState('landing'); // 'landing' | 'chat'
  const [user, setUser] = useState(null); // null | { name, email, avatar, isMember }

  const [messages, setMessages] = useState(INITIAL_CONVERSATION);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState({ online: false, model: '', active: false });

  // Modals state
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);

  // Auth modal state
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [authInitialTab, setAuthInitialTab] = useState('login');

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (currentView === 'chat') {
      scrollToBottom();
    }
  }, [messages, currentView]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/status`)
      .then((res) => res.json())
      .then((data) => {
        setApiStatus({
          online: true,
          model: data.model_primary || '',
          active: data.gemini_active
        });
      })
      .catch(() => {
        setApiStatus({ online: false, model: '', active: false });
      });
  }, []);

  const handleOpenAuth = (tab = 'login') => {
    setAuthInitialTab(tab);
    setIsAuthOpen(true);
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setCurrentView('chat');
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentView('landing');
  };

  const handleSendQuery = async (queryText) => {
    const textToSend = queryText || inputValue.trim();
    if (!textToSend || isLoading) return;

    const newUserMsg = {
      id: Date.now(),
      role: 'user',
      text: textToSend
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          query: textToSend,
          history: messages.map((m) => ({ role: m.role, text: m.text }))
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: data.role || 'assistant',
          text: data.text,
          citations: data.citations,
          isSafetyFallback: data.isSafetyFallback,
          modelUsed: data.modelUsed,
          products: data.products || []
        }
      ]);
    } catch (error) {
      console.error('API Error:', error);

      // Provide informative assistant guidance if the API server is offline / not yet deployed
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          text: `⚠️ **Servidor API de Producción en preparación**\n\nLa interfaz web está activa en Firebase. Para conectar las respuestas de Inteligencia Artificial Gemini en vivo:\n\n1. Inicia el servidor localmente en tu terminal ejecutando: \`python api_server.py\`\n2. O despliega el servicio backend en Render.com usando el archivo \`render.yaml\` del repositorio.\n\n*Recuerda que los navegadores bloquean llamadas desde webs HTTPS a localhost HTTP por motivos de seguridad.*`
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  if (currentView === 'landing') {
    return (
      <>
        <LandingPage
          onOpenAuth={handleOpenAuth}
          onStartChat={() => setCurrentView('chat')}
          user={user}
          onLogout={handleLogout}
        />
        <AuthModal
          isOpen={isAuthOpen}
          onClose={() => setIsAuthOpen(false)}
          onLoginSuccess={handleLoginSuccess}
          initialTab={authInitialTab}
        />
      </>
    );
  }

  return (
    <div className="app-container">
      <header className="chat-header">
        <button className="header-back-btn" onClick={() => setCurrentView('landing')}>
          🏠 Inicio
        </button>
        <div className="avatar">🌿</div>
        <div style={{ flex: 1 }}>
          <h1>Asesor Vademécum Young Living</h1>
          <p>
            Asistente Inteligente de Bienestar & Aromaterapia
          </p>
        </div>

        {user ? (
          <div className="user-profile-badge" style={{ background: 'rgba(255, 255, 255, 0.15)' }}>
            <span className="user-avatar">{user.avatar}</span>
            <span className="user-name">{user.name}</span>
            <button className="btn-logout" onClick={handleLogout} title="Cerrar Sesión">
              🚪
            </button>
          </div>
        ) : (
          <button className="btn-login-ghost" onClick={() => handleOpenAuth('login')}>
            Iniciar Sesión
          </button>
        )}
      </header>

      <main className="chat-messages">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            onSelectProduct={(product) => setSelectedProduct(product)}
          />
        ))}
        {isLoading && (
          <div className="chat-message assistant thinking-bubble">
            <div className="thinking-content">
              <span className="thinking-icon">💭</span>
              <div className="thinking-text">
                <p className="thinking-title"><strong>¡Perfecto! Analizando tu consulta...</strong></p>
                <p className="thinking-sub">🔍 Consultando motor RAG y Gemini 2.5 Flash...</p>
              </div>
              <div className="pulse-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </main>

      <footer className="chat-footer-wrapper">
        <PresetChips onSelectQuery={(query) => handleSendQuery(query)} />
        <div className="chat-input-area">
          <input
            type="text"
            placeholder="Pregunta sobre aceites, recetas, dilución V-6 o seguridad..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendQuery()}
          />
          <button onClick={() => handleSendQuery()} disabled={isLoading}>
            {isLoading ? '...' : 'Enviar'}
          </button>
        </div>
      </footer>

      {/* Modales e Interactividad */}
      <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
      <ArticleModal article={selectedArticle} onClose={() => setSelectedArticle(null)} />
      <AuthModal
        isOpen={isAuthOpen}
        onClose={() => setIsAuthOpen(false)}
        onLoginSuccess={handleLoginSuccess}
        initialTab={authInitialTab}
      />
    </div>
  );
}

export default App;
