import type { Appointment, ChatResponse, Professional } from './types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed with status ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getProfessionals(): Promise<Professional[]> {
  return request<Professional[]>('/api/professionals');
}

export function getAppointments(): Promise<Appointment[]> {
  return request<Appointment[]>('/api/appointments');
}

export function sendQuestion(question: string): Promise<ChatResponse> {
  return request<ChatResponse>('/api/intent', {
    method: 'POST',
    body: JSON.stringify({ question }),
  });
}
