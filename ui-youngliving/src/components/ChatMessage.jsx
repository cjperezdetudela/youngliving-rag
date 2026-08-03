import React from 'react';
import { ProductCard } from './ProductCard';
import { SafetyAlert } from './SafetyAlert';

function FormattedText({ content }) {
  if (!content) return null;

  const lines = content.split('\n');

  return (
    <div className="formatted-text">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="spacer" />;

        // Filter out --- or *** lines completely
        if (/^[-*_]{3,}$/.test(trimmed)) {
          return <div key={idx} className="spacer" />;
        }

        // Clean out any ### or #### symbols if present
        const cleanLine = trimmed.replace(/^#+\s*/, '');

        if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
          const itemText = trimmed.replace(/^[•\-]\s*/, '');
          return (
            <li key={idx} className="list-item">
              {parseBold(itemText)}
            </li>
          );
        }

        return <p key={idx}>{parseBold(cleanLine)}</p>;
      })}
    </div>
  );
}

function parseBold(text) {
  if (!text) return '';
  return text.replace(/\*/g, '');
}

export function ChatMessage({ message, onSelectProduct }) {
  const isAssistant = message.role === 'assistant';

  return (
    <div className={`message ${isAssistant ? 'assistant' : 'user'}`}>
      <div className="message-bubble">
        {isAssistant && (
          <div className="model-badge">
            <span className="badge-icon">🌿</span>
            <span className="badge-name">Asesor Oficial de Aromaterapia</span>
          </div>
        )}

        <FormattedText content={message.text} />
      </div>

      {isAssistant && message.citations && message.citations.length > 0 && (
        <div className="citation-chips">
          <span className="citation-label">Fuentes consultadas:</span>
          {message.citations.map((cite, index) => {
            let label = cite;
            if (cite.includes('Vademecum') || cite.includes('Conocimientos')) label = 'Vademécum Oficial';
            else if (cite.includes('catalogo')) label = 'Catálogo España';
            else if (cite.includes('youngliving_chunks')) label = 'Blog Young Living';
            else if (cite.includes('essenciales')) label = 'Blog Essenciales';
            else if (cite.includes('GENERAL') || cite.includes('SAFETY')) label = 'Guía de Uso Seguro';
            return (
              <span key={index} className="chip">
                {label}
              </span>
            );
          })}
        </div>
      )}
    </div>
  );
}
