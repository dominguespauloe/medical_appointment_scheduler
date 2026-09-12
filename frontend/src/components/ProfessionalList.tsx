import type { Professional } from '../types';

export function ProfessionalList({ professionals }: { professionals: Professional[] }) {
  return (
    <section className="panel">
      <h2>Profissionais</h2>
      <ul className="professional-list">
        {professionals.map((p) => (
          <li key={p.id}>
            <span className="professional-list__name">{p.name}</span>
            <span className="professional-list__speciality">{p.speciality}</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
