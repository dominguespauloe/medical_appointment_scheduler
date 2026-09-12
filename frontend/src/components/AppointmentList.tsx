import type { Appointment } from '../types';

export function AppointmentList({ appointments }: { appointments: Appointment[] }) {
  return (
    <section className="panel">
      <h2>Consultas agendadas</h2>
      {appointments.length === 0 ? (
        <p className="panel__empty">Nenhuma consulta agendada ainda.</p>
      ) : (
        <ul className="appointment-list">
          {appointments.map((a) => (
            <li key={`${a.professionalId}-${a.datetime}-${a.patientName}`}>
              <div className="appointment-list__title">{a.professionalName}</div>
              <div className="appointment-list__meta">
                {new Date(a.datetime).toLocaleString()} · {a.patientName}
              </div>
              {a.reason && <div className="appointment-list__reason">{a.reason}</div>}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
