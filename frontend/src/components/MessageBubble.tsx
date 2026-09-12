import type { ChatMessage } from '../types';

function statusClass(status?: string): string {
  if (status === 'success') return 'bubble bubble--assistant bubble--success';
  if (status === 'error') return 'bubble bubble--assistant bubble--error';
  return 'bubble bubble--assistant';
}

export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === 'user') {
    return (
      <div className="bubble-row bubble-row--user">
        <div className="bubble bubble--user">{message.text}</div>
      </div>
    );
  }

  const data = message.response?.data;
  return (
    <div className="bubble-row bubble-row--assistant">
      <div className={statusClass(message.response?.status)}>
        <p>{message.text}</p>
        {data && data.intent !== 'unknown' && (
          <dl className="bubble-details">
            {data.professionalName && (
              <>
                <dt>Profissional</dt>
                <dd>{data.professionalName}</dd>
              </>
            )}
            {data.datetime && (
              <>
                <dt>Data/Hora</dt>
                <dd>{new Date(data.datetime).toLocaleString()}</dd>
              </>
            )}
            {data.patientName && (
              <>
                <dt>Paciente</dt>
                <dd>{data.patientName}</dd>
              </>
            )}
            {data.reason && (
              <>
                <dt>Motivo</dt>
                <dd>{data.reason}</dd>
              </>
            )}
          </dl>
        )}
      </div>
    </div>
  );
}
