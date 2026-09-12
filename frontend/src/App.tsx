import { useEffect, useState } from 'react';
import './App.css';
import { getAppointments, getProfessionals, sendQuestion } from './api';
import { ChatWindow } from './components/ChatWindow';
import { ProfessionalList } from './components/ProfessionalList';
import { AppointmentList } from './components/AppointmentList';
import type { Appointment, ChatMessage, Professional } from './types';

function App() {
  const [professionals, setProfessionals] = useState<Professional[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getProfessionals(), getAppointments()])
      .then(([profs, appts]) => {
        setProfessionals(profs);
        setAppointments(appts);
      })
      .catch((err: Error) => setLoadError(err.message));
  }, []);

  async function handleSend(question: string) {
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', text: question };
    setMessages((prev) => [...prev, userMessage]);
    setIsSending(true);
    try {
      const response = await sendQuestion(question);
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        text: response.message,
        response,
      };
      setMessages((prev) => [...prev, assistantMessage]);
      if (response.appointment) {
        const appts = await getAppointments();
        setAppointments(appts);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Erro inesperado';
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', text: `Erro: ${message}` },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="app">
      <header className="app__header">
        <h1>Agendamento Médico</h1>
        <p>Identificação de intenção com LangChain + OpenRouter</p>
      </header>

      {loadError && <p className="app__error">Não foi possível conectar à API: {loadError}</p>}

      <main className="app__layout">
        <ChatWindow messages={messages} onSend={handleSend} isSending={isSending} />
        <aside className="app__sidebar">
          <ProfessionalList professionals={professionals} />
          <AppointmentList appointments={appointments} />
        </aside>
      </main>
    </div>
  );
}

export default App;
