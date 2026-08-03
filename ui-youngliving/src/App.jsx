import { useState, useRef, useEffect } from 'react';
import './App.css';
import { ChatMessage } from './components/ChatMessage';
import { PresetChips } from './components/PresetChips';
import { CatalogDrawer } from './components/CatalogDrawer';
import { ProductModal } from './components/ProductModal';
import { ArticleModal } from './components/ArticleModal';
import { API_BASE_URL } from './config';

const INITIAL_CONVERSATION = [
  {
    id: 1,
    role: 'assistant',
    text: '¡Hola! Soy tu **Asesor de Aceites Esenciales y Bienestar**.\n\nCuento con una base de conocimiento oficial de **514 referencias** (273 fichas del Vademécum y Catálogo de España + 241 artículos completos de Blog).\n\n¿En qué te puedo ayudar hoy?'
  }
];

function App() {
  const [messages, setMessages] = useState(INITIAL_CONVERSATION);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState({ online: false, model: '', active: false });

  // Modals state
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [isCatalogOpen, setIsCatalogOpen] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          text: '⚠️ **Error de conexión con el servidor.**\nPor favor, verifica que el servicio esté ejecutándose en el puerto 5000.'
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="chat-header">
        <div className="avatar">🌿</div>
        <div style={{ flex: 1 }}>
          <h1>Asesor Vademécum Young Living & Essenciales</h1>
          <p>
            Catálogo Oficial & Biblioteca de Aromaterapia (514 Referencias)
          </p>
        </div>
        <button className="header-catalog-btn" onClick={() => setIsCatalogOpen(true)}>
          📖 Base de Conocimiento (514)
        </button>
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
                <p className="thinking-title"><strong>¡Perfecto! Déjame ver qué puedo hacer por ti...</strong></p>
                <p className="thinking-sub">🔍 Consultando nuestro Vademécum, catálogo de España y 241 artículos de blog...</p>
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
            placeholder="Pregunta sobre aceites, recetas de blog, dilución V-6 o seguridad..."
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
      <CatalogDrawer
        isOpen={isCatalogOpen}
        onClose={() => setIsCatalogOpen(false)}
        onSelectProduct={(product) => {
          setIsCatalogOpen(false);
          setSelectedProduct(product);
        }}
        onSelectArticle={(article) => {
          setIsCatalogOpen(false);
          setSelectedArticle(article);
        }}
      />
    </div>
  );
}

export default App;
