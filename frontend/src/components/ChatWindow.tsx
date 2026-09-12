import { useRef, useState } from 'react';
import type { FormEvent } from 'react';
import type { ChatMessage } from '../types';
import { MessageBubble } from './MessageBubble';

interface ChatWindowProps {
  messages: ChatMessage[];
  onSend: (question: string) => Promise<void>;
  isSending: boolean;
}

export function ChatWindow({ messages, onSend, isSending }: ChatWindowProps) {
  const [draft, setDraft] = useState('');
  const listEndRef = useRef<HTMLDivElement>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const question = draft.trim();
    if (!question || isSending) return;
    setDraft('');
    await onSend(question);
    listEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }

  return (
    <section className="panel chat">
      <h2>Assistente de Agendamento</h2>
      <div className="chat__messages">
        {messages.length === 0 && (
          <p className="panel__empty">
            Pergunte algo como "Quero agendar com Dr. Carlos Silva amanhã às 16h para Maria
            Santos, motivo check-up".
          </p>
        )}
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        <div ref={listEndRef} />
      </div>
      <form className="chat__form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Digite sua mensagem..."
          disabled={isSending}
        />
        <button type="submit" disabled={isSending || !draft.trim()}>
          {isSending ? 'Enviando...' : 'Enviar'}
        </button>
      </form>
    </section>
  );
}
